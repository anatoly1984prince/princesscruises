import os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=False, slow_mo=150)
        ctx = br.new_context(viewport={'width':1280,'height':900}, locale='en-GB')
        page = ctx.new_page()

        # Step 1 - Go to results page
        page.goto('https://www.princess.com/cruise-search/results/?resType=C', timeout=60000)
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_timeout(3000)

        # Dismiss consent banners
        for cs in ["#onetrust-accept-btn-handler", "button:has-text('Accept All')"]:
            try:
                loc = page.locator(cs)
                if loc.count() > 0 and loc.first.is_visible():
                    print(f"  Dismissing consent: {cs}", flush=True)
                    loc.first.click()
                    page.wait_for_timeout(2000)
                    break
            except:
                pass

        page.wait_for_timeout(8000)
        print(f"Step 1 - Search Results URL: {page.url}", flush=True)
        page.screenshot(path='C:/Users/prote/princess_automation/debug_uk_search.png', full_page=False)
        print("  Screenshot: debug_uk_search.png", flush=True)

        # Find visible itinerary-details link
        links = page.locator("a[href*='itinerary-details']")
        total = links.count()
        print(f"  itinerary-details links (all): {total}", flush=True)

        visible_link = None
        for i in range(total):
            lnk = links.nth(i)
            try:
                if lnk.is_visible():
                    visible_link = lnk
                    break
            except:
                pass

        if visible_link is None:
            print("ERROR: No visible itinerary links found", flush=True)
            br.close()
            return

        href = visible_link.get_attribute('href')
        print(f"  Visible link href: {href}", flush=True)
        visible_link.click(timeout=15000)
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_timeout(4000)
        print(f"Step 2 - Detail URL: {page.url}", flush=True)
        page.screenshot(path='C:/Users/prote/princess_automation/debug_uk_detail.png', full_page=False)
        print("  Screenshot: debug_uk_detail.png", flush=True)

        # Show visible buttons on detail page
        detail_btns = page.evaluate(
            "() => [...document.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null)"
            ".map(e=>(e.innerText||'').trim()).filter(t=>t.length>0 && t.length<60).slice(0,25)"
        )
        print(f"  Visible btns/links on detail: {detail_btns}", flush=True)

        # UK flow: detail page shows stateroom types directly - click Interior (cheapest) then CONTINUE
        # Check for stateroom type buttons on this page
        stateroom_found = False
        for sr_text in ['Interior', 'Oceanview', 'Balcony']:
            sr_btn = page.locator(f"button:has-text('{sr_text}'), [class*='stateroom']:has-text('{sr_text}')").first
            if page.locator(f"button:has-text('{sr_text}')").count() > 0:
                visible = page.locator(f"button:has-text('{sr_text}')").first
                if visible.is_visible():
                    print(f"  Clicking stateroom type on detail page: {sr_text}", flush=True)
                    visible.click(force=True)
                    page.wait_for_timeout(1500)
                    stateroom_found = True
                    break

        # Click CONTINUE on detail page
        cont_btn = page.locator("button:has-text('CONTINUE')")
        if cont_btn.count() > 0 and cont_btn.first.is_visible():
            print(f"  Clicking CONTINUE on detail page", flush=True)
            cont_btn.first.click(timeout=10000)
            page.wait_for_load_state('domcontentloaded')
            page.wait_for_timeout(5000)

        print(f"Step 3 - After detail CONTINUE URL: {page.url}", flush=True)
        page.screenshot(path='C:/Users/prote/princess_automation/debug_uk_after_booknow.png', full_page=False)
        print("  Screenshot: debug_uk_after_booknow.png", flush=True)

        body3 = page.evaluate("() => document.body.innerText.slice(0, 800)")
        print(f"  Body: {body3}", flush=True)

        # Check current step and navigate accordingly
        for step_num in range(4, 12):
            current_url = page.url.lower()
            print(f"Step {step_num} - URL: {page.url}", flush=True)

            if 'guest-count' in current_url:
                print(f"  -> guest-count step", flush=True)
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

            elif 'stateroom-type' in current_url:
                print(f"  -> stateroom-type step", flush=True)
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
                print(f"  After stateroom-type: {page.url}", flush=True)

            elif 'packages' in current_url:
                print(f"  -> packages step", flush=True)
                page.screenshot(path='C:/Users/prote/princess_automation/debug_uk_packages.png', full_page=False)
                print("  Screenshot: debug_uk_packages.png", flush=True)
                pkg_btns = page.evaluate(
                    "() => [...document.querySelectorAll('button')]"
                    ".filter(e=>e.offsetParent!==null)"
                    ".map(e=>(e.innerText||'').trim()).filter(t=>t.length>0)"
                )
                print(f"  Package buttons: {pkg_btns}", flush=True)
                clicked_pkg = False
                for txt in ["I'LL PAY MORE ONBOARD", "PAY MORE ONBOARD", "No Thanks", "Continue", "CONTINUE", "SKIP"]:
                    btn = page.locator('button').filter(has_text=txt)
                    if btn.count() > 0 and btn.first.is_visible():
                        print(f"  Clicking packages btn: '{txt}'", flush=True)
                        btn.first.click()
                        clicked_pkg = True
                        page.wait_for_load_state('domcontentloaded')
                        page.wait_for_timeout(2000)
                        break
                if not clicked_pkg:
                    print(f"  No skip/decline package button found", flush=True)
                    break
                print(f"  After packages: {page.url}", flush=True)

            elif 'stateroom-summary' in current_url:
                print(f"  -> stateroom-summary step", flush=True)
                page.screenshot(path='C:/Users/prote/princess_automation/debug_uk_stateroom_summary.png', full_page=False)
                print("  Screenshot: debug_uk_stateroom_summary.png", flush=True)
                cont = page.locator('button').filter(has_text='CONTINUE')
                if cont.count() > 0 and cont.first.is_visible():
                    print(f"  Clicking CONTINUE on stateroom-summary", flush=True)
                    cont.first.click(timeout=10000)
                    page.wait_for_load_state('domcontentloaded')
                    page.wait_for_timeout(3000)
                    print(f"  After stateroom-summary CONTINUE: {page.url}", flush=True)
                    page.screenshot(path='C:/Users/prote/princess_automation/debug_uk_after_continue.png', full_page=False)
                    print("  Screenshot: debug_uk_after_continue.png", flush=True)
                else:
                    print(f"  No CONTINUE on stateroom-summary", flush=True)
                    break

            elif 'guest' in current_url and 'summary' not in current_url and 'count' not in current_url:
                print(f"  -> GUEST FORM step", flush=True)
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
                page.screenshot(path='C:/Users/prote/princess_automation/debug_uk_guest_form.png', full_page=False)
                print("  Screenshot: debug_uk_guest_form.png", flush=True)
                break

            else:
                print(f"  -> Unrecognized step, showing body text", flush=True)
                body = page.evaluate("() => document.body.innerText.slice(0, 2000)")
                print(f"  Body: {body}", flush=True)
                # Show all visible buttons
                all_btns = page.evaluate(
                    "() => [...document.querySelectorAll('button')]"
                    ".filter(e=>e.offsetParent!==null)"
                    ".map(e=>(e.innerText||'').trim()).filter(t=>t.length>0)"
                )
                print(f"  Visible buttons: {all_btns}", flush=True)
                break

        br.close()

run()
