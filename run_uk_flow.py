from playwright.sync_api import sync_playwright
import sys

def run():
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=False, slow_mo=150)
        ctx = br.new_context(viewport={'width':1280,'height':900}, locale='en-GB')
        page = ctx.new_page()

        # 1. UK cruise search filter page
        page.goto('https://www.princess.com/cruise-search/cruises/', timeout=60000)
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_timeout(3000)
        print(f"Step 1 - Search filter URL: {page.url}", flush=True)

        # Dismiss consent banners
        for consent_sel in ["#onetrust-accept-btn-handler", "button:has-text('Accept All')"]:
            try:
                loc = page.locator(consent_sel)
                if loc.count() > 0 and loc.first.is_visible():
                    print(f"  Dismissing consent: {consent_sel}", flush=True)
                    loc.first.click()
                    page.wait_for_timeout(2000)
                    break
            except:
                pass

        page.wait_for_timeout(5000)

        # Click VIEW RESULTS to load cruise cards
        view_btn = page.locator("button:has-text('VIEW')")
        if view_btn.count() > 0:
            print(f"  Clicking VIEW RESULTS button", flush=True)
            view_btn.first.click()
            page.wait_for_load_state('domcontentloaded')
            page.wait_for_timeout(8000)

        print(f"Step 2 - Results URL: {page.url}", flush=True)
        page.screenshot(path='C:/Users/prote/princess_automation/debug_uk_search.png', full_page=False)
        print("  Screenshot: debug_uk_search.png", flush=True)

        # Get first itinerary-details link
        links = page.locator("a[href*='itinerary-details']")
        print(f"  itinerary-details links: {links.count()}", flush=True)

        if links.count() == 0:
            print("ERROR: No itinerary links found on results page", flush=True)
            # Dump page body
            body = page.evaluate("() => document.body.innerText.slice(0, 2000)")
            print(f"  Page body: {body}", flush=True)
            br.close()
            return

        href = links.first.get_attribute('href')
        print(f"  First link href: {href}", flush=True)
        links.first.click(timeout=15000)
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_timeout(4000)
        print(f"Step 3 - Detail URL: {page.url}", flush=True)
        page.screenshot(path='C:/Users/prote/princess_automation/debug_uk_detail.png', full_page=False)
        print("  Screenshot: debug_uk_detail.png", flush=True)

        # Book Now
        clicked_book = False
        for sel in ["button:has-text('Book Now')", "a:has-text('Book Now')",
                    "button:has-text('BOOK NOW')", "a:has-text('BOOK NOW')"]:
            loc = page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                print(f"  Clicking '{sel}'", flush=True)
                loc.first.click(timeout=10000)
                clicked_book = True
                break
        if not clicked_book:
            print("  No Book Now button found - listing visible buttons", flush=True)
            all_btns = page.evaluate(
                "() => [...document.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null)"
                ".map(e=>e.innerText.trim()).filter(t=>t.length>0).slice(0,30)"
            )
            print(f"  Visible btns/links: {all_btns}", flush=True)

        page.wait_for_load_state('domcontentloaded')
        page.wait_for_timeout(5000)
        print(f"Step 4 - After Book Now URL: {page.url}", flush=True)
        page.screenshot(path='C:/Users/prote/princess_automation/debug_uk_after_booknow.png', full_page=False)
        print("  Screenshot: debug_uk_after_booknow.png", flush=True)

        # Guest count step
        current_url = page.url.lower()
        if 'guest-count' in current_url or ('guest' in current_url and 'count' in current_url):
            print(f"  -> On guest-count step", flush=True)
            btns = page.locator('button.select-pax-btn')
            try:
                btns.first.wait_for(state='visible', timeout=15000)
            except:
                pass
            print(f"  PAX buttons: {btns.count()}", flush=True)
            selected = False
            for i in range(btns.count()):
                b = btns.nth(i)
                if b.is_visible():
                    txt = b.inner_text()
                    print(f"    PAX btn [{i}]: '{txt}'", flush=True)
                    if '2' in txt and not selected:
                        b.click()
                        selected = True
            if not selected and btns.count() > 0:
                btns.first.click()
            page.wait_for_load_state('domcontentloaded')
            page.wait_for_timeout(3000)
            print(f"Step 5 - After guest-count: {page.url}", flush=True)
        else:
            print(f"  Not on guest-count page (URL: {page.url})", flush=True)

        # Stateroom-type step
        current_url = page.url.lower()
        if 'stateroom-type' in current_url:
            print(f"  -> On stateroom-type step", flush=True)
            for t in ['Interior', 'Oceanview', 'Ocean View']:
                tab = page.locator(f"button:has-text('{t}'):not([disabled])")
                if tab.count() > 0 and tab.first.is_visible():
                    print(f"  Clicking stateroom type tab: {t}", flush=True)
                    tab.first.click(force=True)
                    page.wait_for_timeout(1500)
                    break
            sel_btn = page.locator("button:has-text('SELECT')")
            if sel_btn.count() > 0 and sel_btn.first.is_visible():
                sel_btn.first.click()
                page.wait_for_timeout(3000)
            for attempt in range(15):
                sfb = page.locator("button:has-text('Select from'),button:has-text('Select  from')")
                if sfb.count() > 0:
                    for j in range(sfb.count()):
                        b = sfb.nth(j)
                        if b.is_visible():
                            b.click(timeout=10000)
                            break
                    page.wait_for_load_state('domcontentloaded')
                    page.wait_for_timeout(3000)
                    break
                page.wait_for_timeout(1000)
            print(f"Step 6 - After stateroom-type: {page.url}", flush=True)
        else:
            print(f"  Not on stateroom-type page", flush=True)

        # Packages step
        page.wait_for_timeout(2000)
        current_url = page.url.lower()
        if 'packages' in current_url:
            print(f"  -> On packages step: {page.url}", flush=True)
            for txt in ["I'LL PAY MORE ONBOARD", "PAY MORE ONBOARD", "No Thanks", "Continue", "CONTINUE"]:
                btn = page.locator('button').filter(has_text=txt)
                if btn.count() > 0 and btn.first.is_visible():
                    print(f"  Clicking packages btn: '{txt}'", flush=True)
                    btn.first.click()
                    page.wait_for_load_state('domcontentloaded')
                    page.wait_for_timeout(2000)
                    break
            print(f"Step 7 - After packages: {page.url}", flush=True)
        else:
            print(f"  Not on packages page (URL: {page.url})", flush=True)

        # Stateroom summary
        page.wait_for_timeout(2000)
        current_url = page.url.lower()
        print(f"Step 8 - Current URL: {page.url}", flush=True)
        page.screenshot(path='C:/Users/prote/princess_automation/debug_uk_stateroom_summary.png', full_page=False)
        print("  Screenshot: debug_uk_stateroom_summary.png", flush=True)

        if 'stateroom-summary' in current_url:
            print(f"  -> On stateroom-summary", flush=True)
            cont = page.locator('button').filter(has_text='CONTINUE')
            if cont.count() > 0 and cont.first.is_visible():
                print(f"  Clicking CONTINUE on stateroom-summary", flush=True)
                cont.first.click(timeout=10000)
                page.wait_for_load_state('domcontentloaded')
                page.wait_for_timeout(3000)
                print(f"Step 9 - After CONTINUE: {page.url}", flush=True)
                page.screenshot(path='C:/Users/prote/princess_automation/debug_uk_after_continue.png', full_page=False)
                print("  Screenshot: debug_uk_after_continue.png", flush=True)

                # Guest form fields
                if 'guest' in page.url.lower():
                    inputs = page.evaluate(
                        "() => [...document.querySelectorAll('input,select')]"
                        ".filter(e=>e.offsetParent!==null)"
                        ".map(e=>({tag:e.tagName,name:e.name,id:e.id,type:e.type,"
                        "aria:e.getAttribute('aria-label')||'',"
                        "placeholder:e.placeholder||''}))"
                    )
                    print("\n=== Guest form fields ===", flush=True)
                    for inp in inputs:
                        print(inp, flush=True)
                else:
                    print(f"  Not on guest page: {page.url}", flush=True)
                    body = page.evaluate("() => document.body.innerText.slice(0, 2000)")
                    print(f"  Page body: {body}", flush=True)
        else:
            print(f"  Not on stateroom-summary", flush=True)
            # Show all visible buttons and body text
            all_btns = page.evaluate(
                "() => [...document.querySelectorAll('button')]"
                ".filter(e=>e.offsetParent!==null)"
                ".map(e=>e.innerText.trim()).filter(t=>t.length>0)"
            )
            print(f"  Visible buttons: {all_btns}", flush=True)
            body = page.evaluate("() => document.body.innerText.slice(0, 3000)")
            print(f"  Page body text:\n{body}", flush=True)

        br.close()

run()
