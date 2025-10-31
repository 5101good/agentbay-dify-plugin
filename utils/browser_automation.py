"""
AgentBay Browser Automation Module - Using Playwright to Connect to AgentBay Browser
"""
import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    Browser = BrowserContext = Page = None


@dataclass
class BrowserActionResult:
    """Browser action result"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AgentBayBrowserAutomation:
    """AgentBay Browser Automation Class"""

    def __init__(self, endpoint_url: str):
        """
        Initialize browser automation

        Args:
            endpoint_url: AgentBay browser WebSocket endpoint URL
        """
        self.endpoint_url = endpoint_url
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not installed, please run: pip install playwright")

    async def connect(self) -> BrowserActionResult:
        """Connect to AgentBay browser"""
        try:
            # Start playwright (not using context manager)
            if not self.playwright:
                self.playwright = await async_playwright().start()

            # Connect to AgentBay browser via CDP
            self.browser = await self.playwright.chromium.connect_over_cdp(self.endpoint_url)

            # Get or create browser context
            if self.browser.contexts:
                self.context = self.browser.contexts[0]
            else:
                self.context = await self.browser.new_context()

            # Get or create page
            pages = self.context.pages
            if pages:
                self.page = pages[0]
            else:
                self.page = await self.context.new_page()

            # Safely get browser version
            browser_version = "unknown"
            try:
                if hasattr(self.browser, 'version'):
                    version_info = self.browser.version
                    browser_version = version_info if isinstance(version_info, str) else str(version_info)
            except Exception:
                browser_version = "unknown"

            return BrowserActionResult(
                success=True,
                data={
                    'connected': True,
                    'browser_version': browser_version,
                    'pages_count': len(self.context.pages)
                }
            )
        except Exception as e:
            return BrowserActionResult(
                success=False,
                error=f"Failed to connect to browser: {str(e)}"
            )

    async def navigate(self, url: str, wait_time: int = 3) -> BrowserActionResult:
        """Navigate to specified URL"""
        try:
            if not self.page:
                connect_result = await self.connect()
                if not connect_result.success:
                    return connect_result

            # Navigate to URL
            await self.page.goto(url)

            # Wait for page to load
            await self.page.wait_for_timeout(wait_time * 1000)

            # Get page information
            title = await self.page.title()
            current_url = self.page.url

            return BrowserActionResult(
                success=True,
                data={
                    'url': current_url,
                    'title': title,
                    'navigation_time': wait_time
                }
            )
        except Exception as e:
            return BrowserActionResult(
                success=False,
                error=f"Navigation failed: {str(e)}"
            )

    async def screenshot(self, full_page: bool = False) -> BrowserActionResult:
        """Take page screenshot"""
        try:
            if not self.page:
                connect_result = await self.connect()
                if not connect_result.success:
                    return connect_result

            screenshot_data = await self.page.screenshot(full_page=full_page)

            return BrowserActionResult(
                success=True,
                data={
                    'screenshot_data': screenshot_data,
                    'format': 'png',
                    'full_page': full_page,
                    'size': len(screenshot_data)
                }
            )
        except Exception as e:
            return BrowserActionResult(
                success=False,
                error=f"Screenshot failed: {str(e)}"
            )

    async def click_element(self, selector: str) -> BrowserActionResult:
        """Click page element"""
        try:
            if not self.page:
                connect_result = await self.connect()
                if not connect_result.success:
                    return connect_result

            # Wait for element to exist (not requiring visibility)
            await self.page.wait_for_selector(selector, timeout=5000, state='attached')

            # Use forced click directly to avoid visibility check issues
            await self.page.click(selector, force=True, timeout=5000)

            return BrowserActionResult(
                success=True,
                data={
                    'action': 'click',
                    'selector': selector
                }
            )
        except Exception as e:
            return BrowserActionResult(
                success=False,
                error=f"Failed to click element: {str(e)}"
            )

    async def type_text(self, selector: str, text: str) -> BrowserActionResult:
        """Type text into element"""
        try:
            if not self.page:
                connect_result = await self.connect()
                if not connect_result.success:
                    return connect_result

            # Wait for element to exist (not requiring visibility)
            await self.page.wait_for_selector(selector, timeout=5000, state='attached')

            # Use forced fill directly to avoid visibility check issues
            await self.page.fill(selector, text, force=True, timeout=5000)

            return BrowserActionResult(
                success=True,
                data={
                    'action': 'type',
                    'selector': selector,
                    'text': text
                }
            )
        except Exception as e:
            return BrowserActionResult(
                success=False,
                error=f"Failed to type text: {str(e)}"
            )

    async def get_page_content(self) -> BrowserActionResult:
        """Get page content"""
        try:
            if not self.page:
                connect_result = await self.connect()
                if not connect_result.success:
                    return connect_result

            title = await self.page.title()
            url = self.page.url
            content = await self.page.content()

            return BrowserActionResult(
                success=True,
                data={
                    'title': title,
                    'url': url,
                    'content': content,
                    'content_length': len(content)
                }
            )
        except Exception as e:
            return BrowserActionResult(
                success=False,
                error=f"Failed to get page content: {str(e)}"
            )

    async def analyze_page_elements(self, element_types: list = None) -> BrowserActionResult:
        """Analyze page elements to help AI understand page structure"""
        try:
            if not self.page:
                connect_result = await self.connect()
                if not connect_result.success:
                    return connect_result

            if element_types is None:
                element_types = ['input', 'button', 'a', 'form']

            elements_info = {}

            for element_type in element_types:
                elements = await self.page.query_selector_all(element_type)
                element_list = []

                for i, element in enumerate(elements):
                    try:
                        # Get element basic information
                        tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                        element_id = await element.get_attribute('id')
                        element_class = await element.get_attribute('class')
                        element_name = await element.get_attribute('name')
                        element_type_attr = await element.get_attribute('type')
                        element_value = await element.get_attribute('value')
                        placeholder = await element.get_attribute('placeholder')
                        text_content = await element.text_content()

                        # Get element visibility
                        is_visible = await element.is_visible()

                        element_info = {
                            'index': i,
                            'tag': tag_name,
                            'id': element_id,
                            'class': element_class,
                            'name': element_name,
                            'type': element_type_attr,
                            'value': element_value,
                            'placeholder': placeholder,
                            'text': text_content,
                            'visible': is_visible
                        }

                        # Generate possible selectors
                        selectors = []
                        if element_id:
                            selectors.append(f"#{element_id}")
                        if element_name:
                            selectors.append(f"[name='{element_name}']")
                        if element_class:
                            class_selector = f".{element_class.replace(' ', '.')}"
                            selectors.append(class_selector)
                        selectors.append(f"{tag_name}:nth-child({i+1})")

                        element_info['possible_selectors'] = selectors
                        element_list.append(element_info)

                    except Exception:
                        # Skip if element analysis fails
                        continue

                elements_info[element_type] = element_list

            return BrowserActionResult(
                success=True,
                data={
                    'elements': elements_info,
                    'total_elements': sum(len(elements) for elements in elements_info.values())
                }
            )
        except Exception as e:
            return BrowserActionResult(
                success=False,
                error=f"Failed to analyze page elements: {str(e)}"
            )

    async def scroll_page(self, direction: str = "down", distance: int = 500) -> BrowserActionResult:
        """Scroll page"""
        try:
            if not self.page:
                connect_result = await self.connect()
                if not connect_result.success:
                    return connect_result

            if direction == "down":
                await self.page.evaluate(f"window.scrollBy(0, {distance})")
            elif direction == "up":
                await self.page.evaluate(f"window.scrollBy(0, -{distance})")
            elif direction == "top":
                await self.page.evaluate("window.scrollTo(0, 0)")
            elif direction == "bottom":
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

            return BrowserActionResult(
                success=True,
                data={
                    'action': 'scroll',
                    'direction': direction,
                    'distance': distance
                }
            )
        except Exception as e:
            return BrowserActionResult(
                success=False,
                error=f"Failed to scroll page: {str(e)}"
            )

    async def wait_for_element(self, selector: str, timeout: int = 5000) -> BrowserActionResult:
        """Wait for element to appear"""
        try:
            if not self.page:
                connect_result = await self.connect()
                if not connect_result.success:
                    return connect_result

            await self.page.wait_for_selector(selector, timeout=timeout)

            return BrowserActionResult(
                success=True,
                data={
                    'action': 'wait_for_element',
                    'selector': selector,
                    'timeout': timeout
                }
            )
        except Exception as e:
            return BrowserActionResult(
                success=False,
                error=f"Failed to wait for element: {str(e)}"
            )

    async def close(self) -> BrowserActionResult:
        """Close browser connection"""
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
                self.context = None
                self.page = None

            if self.playwright:
                await self.playwright.stop()
                self.playwright = None

            return BrowserActionResult(
                success=True,
                data={'closed': True}
            )
        except Exception as e:
            return BrowserActionResult(
                success=False,
                error=f"Failed to close browser: {str(e)}"
            )


def run_browser_action(endpoint_url: str, action_func, *args, **kwargs):
    """
    Run browser operation synchronously

    Args:
        endpoint_url: Browser endpoint URL
        action_func: Async operation function to execute
        *args, **kwargs: Parameters passed to operation function

    Returns:
        BrowserActionResult: Operation result
    """
    async def _run():
        automation = AgentBayBrowserAutomation(endpoint_url)
        try:
            return await action_func(automation, *args, **kwargs)
        finally:
            await automation.close()

    # Use simpler but more reliable method: always run in new thread
    import concurrent.futures

    def run_in_new_thread():
        # Create new event loop in new thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(_run())
        finally:
            loop.close()

    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_new_thread)
            return future.result(timeout=60)  # 60 seconds timeout
    except Exception as e:
        return BrowserActionResult(
            success=False,
            error=f"Failed to run browser operation: {str(e)}"
        )


# Predefined common operation functions
async def navigate_and_screenshot(automation: AgentBayBrowserAutomation, url: str, wait_time: int = 3):
    """Navigate and take screenshot"""
    nav_result = await automation.navigate(url, wait_time)
    if not nav_result.success:
        return nav_result

    screenshot_result = await automation.screenshot(full_page=True)

    return BrowserActionResult(
        success=True,
        data={
            'navigation': nav_result.data,
            'screenshot': screenshot_result.data if screenshot_result.success else None
        }
    )


async def search_and_screenshot(automation: AgentBayBrowserAutomation, url: str, search_selector: str, search_text: str, wait_time: int = 3):
    """Search and take screenshot"""
    # Navigate to page
    nav_result = await automation.navigate(url, wait_time)
    if not nav_result.success:
        return nav_result

    # Input search text
    type_result = await automation.type_text(search_selector, search_text)
    if not type_result.success:
        return type_result

    # Press Enter to search
    await automation.page.keyboard.press("Enter")
    await automation.page.wait_for_timeout(2000)

    # Take screenshot
    screenshot_result = await automation.screenshot(full_page=True)

    return BrowserActionResult(
        success=True,
        data={
            'navigation': nav_result.data,
            'search': type_result.data,
            'screenshot': screenshot_result.data if screenshot_result.success else None
        }
    )