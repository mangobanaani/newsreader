"""OCR and web scraping service."""

import hashlib
import io
from typing import Any

import aiohttp
from PIL import Image
from sqlalchemy.orm import Session

from app.models.scraper import ScrapedContent, ScraperDestination


class OCRScraper:
    """OCR and content scraping service."""

    def __init__(self, db: Session):
        """Initialize OCR scraper."""
        self.db = db

    async def scrape_destination(self, destination: ScraperDestination) -> ScrapedContent:
        """Scrape content from destination."""
        content = ScrapedContent(
            destination_id=destination.id,
            source_url=destination.source_url,
            processing_status="processing",
        )
        self.db.add(content)

        try:
            if destination.source_type == "image_url":
                await self._scrape_image(destination, content)
            elif destination.source_type == "pdf_url":
                await self._scrape_pdf(destination, content)
            elif destination.source_type == "web_page":
                await self._scrape_webpage(destination, content)
            elif destination.source_type == "screenshot":
                await self._scrape_screenshot(destination, content)

            content.processing_status = "completed"

        except Exception as e:
            content.processing_status = "failed"
            if content.processing_errors is None:
                content.processing_errors = []
            content.processing_errors.append(str(e))

        self.db.commit()
        return content

    async def _scrape_image(self, destination: ScraperDestination, content: ScrapedContent) -> None:
        """Scrape and OCR an image."""
        async with aiohttp.ClientSession() as session:
            headers = destination.custom_headers or {}
            async with session.get(destination.source_url, headers=headers) as response:
                image_data = await response.read()

        # Load image
        image = Image.open(io.BytesIO(image_data))

        # Preprocess image if needed
        if destination.ocr_preprocessing:
            image = self._preprocess_image(image, destination.ocr_preprocessing)

        # Perform OCR
        if destination.ocr_enabled:
            ocr_result = self._perform_ocr(image, destination.ocr_languages)
            content.ocr_text = ocr_result["text"]
            content.ocr_confidence = ocr_result["confidence"]
            content.ocr_metadata = ocr_result["metadata"]
            content.content_text = ocr_result["text"]

        # Calculate content hash for deduplication
        content.content_hash = hashlib.md5((content.ocr_text or "").encode()).hexdigest()

    async def _scrape_pdf(self, destination: ScraperDestination, content: ScrapedContent) -> None:
        """Scrape and extract text from PDF."""
        async with aiohttp.ClientSession() as session:
            headers = destination.custom_headers or {}
            async with session.get(destination.source_url, headers=headers) as response:
                pdf_data = await response.read()

        # Extract text from PDF
        try:
            import pypdf

            pdf_reader = pypdf.PdfReader(io.BytesIO(pdf_data))
            extracted_text = []

            for page in pdf_reader.pages:
                page_text = page.extract_text()
                extracted_text.append(page_text)

                # OCR if text extraction fails or OCR is explicitly enabled
                if destination.ocr_enabled and len(page_text.strip()) < 50:
                    # Convert page to image and OCR
                    # Note: This requires additional dependencies
                    pass

            content.content_text = "\n\n".join(extracted_text)
            content.content_hash = hashlib.md5(content.content_text.encode()).hexdigest()

        except ImportError:
            content.processing_errors.append("pypdf not installed - cannot extract PDF text")

    async def _scrape_webpage(
        self, destination: ScraperDestination, content: ScrapedContent
    ) -> None:
        """Scrape content from web page."""
        async with aiohttp.ClientSession() as session:
            headers = destination.custom_headers or {}
            async with session.get(destination.source_url, headers=headers) as response:
                html_content = await response.text()

        content.content_html = html_content

        # Parse HTML and extract content
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, "html.parser")

            # Extract based on CSS selectors
            if destination.css_selectors:
                extracted_parts = []
                for key, selector in destination.css_selectors.items():
                    elements = soup.select(selector)
                    for elem in elements:
                        extracted_parts.append(elem.get_text())

                content.content_text = "\n\n".join(extracted_parts)

                # Extract title
                if "title" in destination.css_selectors:
                    title_elem = soup.select_one(destination.css_selectors["title"])
                    if title_elem:
                        content.title = title_elem.get_text().strip()
            else:
                # Default extraction
                content.content_text = soup.get_text()
                title_tag = soup.find("title")
                if title_tag:
                    content.title = title_tag.get_text().strip()

            # Extract images if requested
            if destination.extract_images:
                images = soup.find_all("img")
                content.extracted_images = [img.get("src") for img in images if img.get("src")]

            # Extract links if requested
            if destination.extract_links:
                links = soup.find_all("a")
                content.extracted_links = [a.get("href") for a in links if a.get("href")]

            # Clean HTML if requested
            if destination.clean_html:
                content.content_text = self._clean_text(content.content_text)

            content.content_hash = hashlib.md5((content.content_text or "").encode()).hexdigest()

        except ImportError:
            content.processing_errors.append("BeautifulSoup not installed - cannot parse HTML")

    async def _scrape_screenshot(
        self, destination: ScraperDestination, content: ScrapedContent
    ) -> None:
        """Take screenshot and perform OCR."""
        # This requires playwright or selenium
        # Placeholder implementation
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.goto(destination.source_url)

                # Take screenshot
                screenshot_bytes = await page.screenshot()
                await browser.close()

                # Load screenshot as image
                image = Image.open(io.BytesIO(screenshot_bytes))

                # Perform OCR
                if destination.ocr_enabled:
                    ocr_result = self._perform_ocr(image, destination.ocr_languages)
                    content.ocr_text = ocr_result["text"]
                    content.ocr_confidence = ocr_result["confidence"]
                    content.content_text = ocr_result["text"]

        except ImportError:
            content.processing_errors.append("Playwright not installed - cannot take screenshots")

    def _preprocess_image(self, image: Image.Image, options: dict[str, Any]) -> Image.Image:
        """Preprocess image for better OCR results."""
        # Convert to grayscale
        if options.get("grayscale", False):
            image = image.convert("L")

        # Increase contrast
        if options.get("contrast", 0) > 0:
            from PIL import ImageEnhance

            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1 + options["contrast"])

        # Resize if needed
        if "scale" in options:
            scale = options["scale"]
            new_size = (
                int(image.width * scale),
                int(image.height * scale),
            )
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        # Denoise
        if options.get("denoise", False):
            from PIL import ImageFilter

            image = image.filter(ImageFilter.MedianFilter(size=3))

        return image

    def _perform_ocr(self, image: Image.Image, languages: list[str]) -> dict[str, Any]:
        """Perform OCR on image using Tesseract."""
        try:
            import pytesseract

            # Configure Tesseract
            lang_string = "+".join(languages)

            # Get detailed OCR data
            ocr_data = pytesseract.image_to_data(
                image, lang=lang_string, output_type=pytesseract.Output.DICT
            )

            # Extract text
            text = pytesseract.image_to_string(image, lang=lang_string)

            # Calculate average confidence
            confidences = [int(conf) for conf in ocr_data["conf"] if conf != "-1"]
            avg_confidence = int(sum(confidences) / len(confidences)) if confidences else 0

            return {
                "text": text.strip(),
                "confidence": avg_confidence,
                "metadata": {
                    "languages": languages,
                    "word_count": len(text.split()),
                },
            }

        except ImportError:
            return {
                "text": "",
                "confidence": 0,
                "metadata": {"error": "pytesseract not installed"},
            }

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        import re

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove special characters but keep basic punctuation
        text = re.sub(r"[^\w\s.,!?;:()\-\"]", "", text)

        return text.strip()
