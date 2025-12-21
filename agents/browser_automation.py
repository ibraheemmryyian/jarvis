"""
Browser Automation for Jarvis
Playwright-based web interaction for testing and scraping.
"""
import os
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class BrowserResult:
    success: bool
    data: any
    error: str = None
    screenshot_path: str = None


class BrowserAutomation:
    """
    Web automation using Playwright.
    
    Features:
    - Screenshot capture
    - Form interaction
    - Content extraction
    - Responsive testing
    - Link validation
    """
    
    def __init__(self):
        self.browser = None
        self.context = None
        self._playwright = None
        self._initialized = False
    
    async def _ensure_browser(self):
        """Lazy initialization of browser."""
        if not self._initialized:
            try:
                from playwright.async_api import async_playwright
                self._playwright = await async_playwright().start()
                self.browser = await self._playwright.chromium.launch(headless=True)
                self.context = await self.browser.new_context(
                    viewport={"width": 1920, "height": 1080}
                )
                self._initialized = True
            except ImportError:
                raise ImportError("Playwright not installed. Run: pip install playwright && playwright install chromium")
    
    async def take_screenshot(self, url: str, output_path: str = None, 
                             viewport: Dict = None) -> BrowserResult:
        """
        Take a screenshot of a URL.
        
        Args:
            url: URL to capture
            output_path: Where to save screenshot (auto-generated if None)
            viewport: Optional viewport size {"width": x, "height": y}
        """
        try:
            await self._ensure_browser()
            
            page = await self.context.new_page()
            
            if viewport:
                await page.set_viewport_size(viewport)
            
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            if not output_path:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"screenshot_{timestamp}.png"
            
            await page.screenshot(path=output_path, full_page=True)
            await page.close()
            
            return BrowserResult(
                success=True,
                data={"path": output_path, "url": url},
                screenshot_path=output_path
            )
        except Exception as e:
            return BrowserResult(success=False, data=None, error=str(e))
    
    async def extract_content(self, url: str, selector: str = None) -> BrowserResult:
        """
        Extract content from a webpage.
        
        Args:
            url: URL to scrape
            selector: CSS selector for specific content (None = full page text)
        """
        try:
            await self._ensure_browser()
            
            page = await self.context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            if selector:
                elements = await page.query_selector_all(selector)
                content = [await el.text_content() for el in elements]
            else:
                content = await page.text_content("body")
            
            await page.close()
            
            return BrowserResult(success=True, data=content)
        except Exception as e:
            return BrowserResult(success=False, data=None, error=str(e))
    
    async def fill_form(self, url: str, form_data: Dict[str, str],
                        submit_selector: str = None) -> BrowserResult:
        """
        Fill and optionally submit a form.
        
        Args:
            url: URL with the form
            form_data: Dict of {selector: value} to fill
            submit_selector: Optional submit button selector
        """
        try:
            await self._ensure_browser()
            
            page = await self.context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            for selector, value in form_data.items():
                await page.fill(selector, value)
            
            if submit_selector:
                await page.click(submit_selector)
                await page.wait_for_load_state("networkidle")
            
            final_url = page.url
            content = await page.text_content("body")
            
            await page.close()
            
            return BrowserResult(
                success=True,
                data={"final_url": final_url, "content_preview": content[:500]}
            )
        except Exception as e:
            return BrowserResult(success=False, data=None, error=str(e))
    
    async def check_responsive(self, url: str, 
                               viewports: List[Dict] = None) -> BrowserResult:
        """
        Test page at multiple viewport sizes.
        
        Args:
            url: URL to test
            viewports: List of {"name": x, "width": y, "height": z}
        """
        if not viewports:
            viewports = [
                {"name": "mobile", "width": 375, "height": 812},
                {"name": "tablet", "width": 768, "height": 1024},
                {"name": "desktop", "width": 1920, "height": 1080},
            ]
        
        results = []
        
        try:
            await self._ensure_browser()
            
            for vp in viewports:
                page = await self.context.new_page()
                await page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
                
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Check for horizontal overflow
                has_overflow = await page.evaluate("""
                    () => document.body.scrollWidth > window.innerWidth
                """)
                
                screenshot_path = f"responsive_{vp['name']}.png"
                await page.screenshot(path=screenshot_path)
                
                results.append({
                    "viewport": vp["name"],
                    "width": vp["width"],
                    "height": vp["height"],
                    "has_horizontal_overflow": has_overflow,
                    "screenshot": screenshot_path
                })
                
                await page.close()
            
            return BrowserResult(success=True, data=results)
        except Exception as e:
            return BrowserResult(success=False, data=None, error=str(e))
    
    async def test_links(self, url: str) -> BrowserResult:
        """
        Test all links on a page for broken links.
        """
        try:
            await self._ensure_browser()
            
            page = await self.context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            links = await page.query_selector_all("a[href]")
            
            results = {"valid": [], "broken": [], "external": []}
            
            for link in links[:50]:  # Limit to first 50 links
                href = await link.get_attribute("href")
                if not href or href.startswith("#") or href.startswith("javascript:"):
                    continue
                
                if href.startswith("http") and url.split("/")[2] not in href:
                    results["external"].append(href)
                    continue
                
                # Test internal links
                try:
                    full_url = href if href.startswith("http") else f"{url.rstrip('/')}/{href.lstrip('/')}"
                    response = await page.goto(full_url, timeout=10000)
                    
                    if response and response.status < 400:
                        results["valid"].append(href)
                    else:
                        results["broken"].append({"url": href, "status": response.status if response else "no response"})
                except:
                    results["broken"].append({"url": href, "error": "timeout"})
            
            await page.close()
            
            return BrowserResult(success=True, data=results)
        except Exception as e:
            return BrowserResult(success=False, data=None, error=str(e))
    
    async def close(self):
        """Clean up browser resources."""
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._initialized = False


# Sync wrapper for non-async usage
class BrowserAutomationSync:
    """Synchronous wrapper for BrowserAutomation."""
    
    def __init__(self):
        self._async = BrowserAutomation()
    
    def _run(self, coro):
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    
    def take_screenshot(self, url: str, output_path: str = None, 
                        viewport: Dict = None) -> BrowserResult:
        return self._run(self._async.take_screenshot(url, output_path, viewport))
    
    def extract_content(self, url: str, selector: str = None) -> BrowserResult:
        return self._run(self._async.extract_content(url, selector))
    
    def fill_form(self, url: str, form_data: Dict[str, str],
                  submit_selector: str = None) -> BrowserResult:
        return self._run(self._async.fill_form(url, form_data, submit_selector))
    
    def check_responsive(self, url: str, viewports: List[Dict] = None) -> BrowserResult:
        return self._run(self._async.check_responsive(url, viewports))
    
    def test_links(self, url: str) -> BrowserResult:
        return self._run(self._async.test_links(url))
    
    def close(self):
        self._run(self._async.close())


# Singleton
try:
    browser_automation = BrowserAutomationSync()
except:
    browser_automation = None
    print("[BrowserAutomation] Playwright not available. Install with: pip install playwright && playwright install chromium")
