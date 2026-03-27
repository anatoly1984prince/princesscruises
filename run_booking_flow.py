import sys, os
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch(headless=False, slow_mo=200)
    ctx = br.new_context(viewport={'width': 1280, 'height': 900}, locale='en-US')
    page = ctx.new_page()

    # ---- Step 1: Cruise search ----
    print("Step 1: Loading cruise search...")
    page.goto('https://www.princess.com/cruise-search/', timeout=60000)
    page.wait_for_load_state('domcontentloaded')
    page.wait_for_timeout(6000)

    # Click Alaska destination
    alaska = page.locator("text=Alaska").first
    if alaska.is_visible():
        alaska.click()
        page.wait_for_timeout(2000)

    # Click VIEW RESULTS
    for btn_sel in ["button:has-text('RESULTS')", "button:has-text('Results')"]:
        loc = page.locator(btn_sel)
        if loc.count() > 0 and loc.first.is_visible():
            print(f"  Clicking: '{loc.first.inner_text()}'")
            loc.first.click()
            page.wait_for_load_state('domcontentloaded')
            page.wait_for_timeout(8000)
            break

    print(f"  Results URL: {page.url}")

    # ---- Step 2: Click first itinerary-details link ----
    print("Step 2: Clicking first itinerary-details link...")
    links = page.locator("a[href*='itinerary-details']")
    links.first.wait_for(state='visible', timeout=15000)
    links.first.click(timeout=15000)
    page.wait_for_load_state('domcontentloaded')
    page.wait_for_timeout(4000)
    print(f"  Itinerary URL: {page.url}")

    # ---- Step 3: Click Book Now / Continue ----
    print("Step 3: Clicking Book Now / Continue...")
    for sel in [
        "button:has-text('Book Now')", "a:has-text('Book Now')",
        "button:has-text('BOOK NOW')", "a:has-text('BOOK NOW')",
        "button:has-text('CONTINUE')", "button:has-text('Continue')",
        "button:has-text('BOOK')", "a:has-text('Book')"
    ]:
        loc = page.locator(sel)
        if loc.count() > 0 and loc.first.is_visible():
            txt = loc.first.inner_text()
            print(f"  Found: '{txt}' clicking")
            loc.first.click(timeout=10000)
            break
    page.wait_for_load_state('domcontentloaded')
    page.wait_for_timeout(4000)
    print(f"  Post-book URL: {page.url}")

    # ---- Step 4: Guest count page ----
    if 'guest-count' in page.url.lower():
        print("Step 4: Guest count page...")
        btns = page.locator('button.select-pax-btn')
        if btns.count() == 0:
            btns = page.locator("button").filter(has_text="2")
        btns.first.wait_for(state='visible', timeout=15000)
        clicked = False
        for i in range(btns.count()):
            b = btns.nth(i)
            if b.is_visible() and '2' in b.inner_text():
                print("  Clicking 2 guests button")
                b.click()
                clicked = True
                break
        if not clicked:
            btns.first.click()
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_timeout(4000)
        print(f"  Post-guest URL: {page.url}")

    # ---- Step 5: Stateroom type ----
    if 'stateroom-type' in page.url.lower():
        print("Step 5: Stateroom type page...")
        # Interior may already be selected; try clicking it with force, or skip if already selected
        for t in ['Interior', 'Oceanview', 'Balcony']:
            tab = page.locator(f"button:has-text('{t}')")
            if tab.count() > 0 and tab.first.is_visible():
                print(f"  Clicking '{t}' tab (force=True)")
                try:
                    tab.first.click(force=True, timeout=5000)
                except Exception as ex:
                    print(f"  Tab click error (continuing): {ex}")
                page.wait_for_timeout(2000)
                break

        # Click SELECT on a cabin
        sel_btn = page.locator("button:has-text('SELECT')")
        if sel_btn.count() > 0 and sel_btn.first.is_visible():
            print("  Clicking SELECT")
            sel_btn.first.click(force=True)
            page.wait_for_timeout(3000)

        # Click "Select from $xxx"
        for attempt in range(20):
            sfb = page.locator("button:has-text('Select from'), button:has-text('Select  from')")
            if sfb.count() > 0:
                for j in range(sfb.count()):
                    b = sfb.nth(j)
                    if b.is_visible():
                        print(f"  Clicking 'Select from' (attempt {attempt+1})")
                        b.click(timeout=10000)
                        break
                page.wait_for_load_state('domcontentloaded')
                page.wait_for_timeout(4000)
                break
            page.wait_for_timeout(1000)

        print(f"  Post-stateroom URL: {page.url}")

    # ---- Step 6: Packages page ----
    page.wait_for_timeout(2000)
    if 'packages' in page.url.lower() or 'package' in page.url.lower():
        print("Step 6: Packages page...")
        for txt in ["PAY MORE ONBOARD", "No Thanks", "No, thanks", "SKIP", "Continue", "CONTINUE"]:
            btn = page.locator("button").filter(has_text=txt)
            if btn.count() > 0 and btn.first.is_visible():
                print(f"  Clicking '{txt}'")
                btn.first.click()
                page.wait_for_load_state('domcontentloaded')
                page.wait_for_timeout(3000)
                break
        print(f"  Post-packages URL: {page.url}")

    # ---- Step 7: Capture final state ----
    page.wait_for_timeout(3000)
    final_url = page.url
    print(f"\nFinal URL: {final_url}")
    page.screenshot(path='debug_stateroom_summary_login.png', full_page=True)
    print("Screenshot saved: debug_stateroom_summary_login.png")

    # Get ALL interactive elements
    elements = page.evaluate("""() => {
        const els = [...document.querySelectorAll('a, button, input[type=submit], input[type=button]')];
        return els
            .filter(el => el.offsetParent !== null)
            .map(el => ({
                tag: el.tagName,
                text: (el.innerText || '').trim().substring(0, 80),
                href: el.href || '',
                id: el.id || '',
                cls: (el.className || '').substring(0, 80),
                aria: el.getAttribute('aria-label') || '',
                name: el.getAttribute('name') || ''
            }))
            .filter(el => el.text || el.aria);
    }""")

    print(f"\n=== All visible interactive elements ({len(elements)} total) on {final_url} ===")
    for e in elements:
        print(e)

    # Specifically filter login/signin related
    print("\n=== LOGIN / SIGN-IN related elements ===")
    keywords = ['sign', 'login', 'log in', 'account', 'member', 'captain', 'circle', 'join', 'register', 'auth']
    login_els = [e for e in elements if any(k in (e['text'] + e['href'] + e['id'] + e['cls'] + e['aria']).lower() for k in keywords)]
    for e in login_els:
        print(e)

    # Also check for modal/overlay/form elements
    modal_info = page.evaluate("""() => {
        const modals = [...document.querySelectorAll('[class*=modal], [class*=overlay], [class*=dialog], [role=dialog]')];
        return modals
            .filter(m => m.offsetParent !== null)
            .map(m => ({
                tag: m.tagName,
                cls: (m.className || '').substring(0, 100),
                role: m.getAttribute('role') || '',
                visible: m.offsetParent !== null,
                innerText: (m.innerText || '').trim().substring(0, 200)
            }));
    }""")
    print(f"\n=== Modal/Overlay/Dialog elements ({len(modal_info)} found) ===")
    for m in modal_info:
        print(m)

    # Check for input fields (login form inputs)
    inputs = page.evaluate("""() => {
        const els = [...document.querySelectorAll('input')];
        return els
            .filter(el => el.offsetParent !== null)
            .map(el => ({
                type: el.type,
                name: el.name,
                id: el.id,
                placeholder: el.placeholder,
                cls: (el.className || '').substring(0, 80)
            }));
    }""")
    print(f"\n=== Visible input fields ({len(inputs)} found) ===")
    for inp in inputs:
        print(inp)

    br.close()
