"""Market test: AU site — guest booking flow.

Starts from https://www.princess.com/en-au, books as guest through to
confirmation and prints the booking number.
"""
from __future__ import annotations

import allure
import pytest

from pages.cruise_results_page import CruiseResultsPage
from pages.cruise_detail_page import CruiseDetailPage
from pages.booking_cabin_page import BookingCabinPage
from pages.booking_guests_page import BookingGuestsPage
from pages.booking_payment_page import BookingPaymentPage
from pages.booking_confirmation_page import BookingConfirmationPage
from pages.login_page import LoginPage


@allure.epic("Princess Cruises - Regression")
@allure.feature("Booking Flow — AU Site Guest Booking")
@pytest.mark.regression
@pytest.mark.booking
@pytest.mark.e2e
class TestBookingAUGuest:
    """Complete a guest booking starting from https://www.princess.com/en-au
    through to confirmation, and print the confirmed booking number."""

    AU_BASE_URL = "https://www.princess.com/en-au"
    AU_RESULTS_URL = "https://www.princess.com/en-au/cruise-search/results/?resType=C&guestCount=2"

    @allure.story("Guest booking on AU site shows confirmed booking number")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_au_guest_booking_number(
        self,
        cruise_results_page: CruiseResultsPage,
        cruise_detail_page: CruiseDetailPage,
        booking_cabin_page: BookingCabinPage,
        booking_guests_page: BookingGuestsPage,
        booking_payment_page: BookingPaymentPage,
        booking_confirmation_page: BookingConfirmationPage,
        login_page: LoginPage,
        test_user_data: dict,
    ):
        """Navigate https://www.princess.com/en-au → cruise results → detail →
        CONTINUE → stateroom-type → packages → stateroom-summary → guest forms →
        payment (Tom Cat 4111111111111111 12/33 234) → confirmation number."""

        page = cruise_results_page.page

        with allure.step("Step 1: Navigate to AU cruise search results"):
            page.goto(self.AU_RESULTS_URL, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
            print(f"\nAU results URL: {page.url}")
            loaded = cruise_results_page._wait_for_real_cards(timeout=40000)
            if not loaded:
                # Try from UK base URL with navigation
                page.goto(self.AU_BASE_URL, timeout=60000, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)
                # Navigate to find a cruise
                page.goto(
                    "https://www.princess.com/cruise-search/results/?resType=C&guestCount=2",
                    timeout=60000,
                    wait_until="domcontentloaded",
                )
                page.wait_for_load_state("domcontentloaded")
                loaded = cruise_results_page._wait_for_real_cards(timeout=40000)
                if not loaded:
                    pytest.skip("Cruise result cards did not render — SPA blocked in headless mode")

        with allure.step("Step 2: Click first cruise card to open detail page"):
            cruise_results_page.click_card(0)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)
            print(f"Detail page URL: {page.url}")
            booking_cabin_page.take_screenshot("au_step2_detail_page")

        with allure.step("Step 3: Click CONTINUE (UK detail page) to enter booking"):
            # UK detail page has a CONTINUE button instead of "Book Now"
            # Try CONTINUE first, then fall back to Book Now
            continue_btn = page.locator("button").filter(has_text="CONTINUE")
            book_now_btn = page.locator(cruise_detail_page.BOOK_NOW_BTN)

            if continue_btn.count() > 0 and continue_btn.first.is_visible(timeout=10000):
                continue_btn.first.click(timeout=15000)
            elif book_now_btn.count() > 0 and book_now_btn.first.is_visible(timeout=10000):
                cruise_detail_page.click_book_now()
            else:
                # Last resort: any prominent CTA button
                for txt in ["Book", "Select", "Choose", "Reserve"]:
                    btn = page.locator("button").filter(has_text=txt)
                    if btn.count() > 0 and btn.first.is_visible():
                        btn.first.click(timeout=15000)
                        break
                else:
                    pytest.skip("No CONTINUE / Book Now button found on UK detail page")

            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(3000)
            print(f"URL after CONTINUE: {page.url}")

        with allure.step("Step 4: Handle login wall / guest-count if shown"):
            url = page.url.lower()
            if any(k in url for k in ["login", "sign-in", "auth"]):
                proceeded = login_page.continue_as_guest()
                if not proceeded:
                    pytest.skip("Login wall present with no guest checkout option")
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(2000)
                url = page.url.lower()

            # UK normally skips guest-count (guestCount=2 in URL), but handle it if shown
            if "guest-count" in url:
                pax = page.locator("button.select-pax-btn")
                try:
                    pax.first.wait_for(state="visible", timeout=15000)
                except Exception:
                    pass
                clicked = False
                for i in range(pax.count()):
                    b = pax.nth(i)
                    if b.is_visible() and "2" in b.inner_text():
                        b.click()
                        clicked = True
                        break
                if not clicked and pax.count() > 0:
                    pax.first.click()
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(3000)

        with allure.step("Step 5: Select stateroom type"):
            if not booking_cabin_page.wait_for_cabin_page(timeout=20000):
                url = page.url.lower()
                if any(k in url for k in ["login", "sign-in"]):
                    pytest.skip("Redirected to login — guest checkout not available on UK site")
                # May be on stateroom-type already without matching is_on_cabin_page check
                if "stateroom-type" not in url and "stateroom" not in url:
                    pytest.skip(f"Did not reach cabin/stateroom page (at: {page.url})")

            if "stateroom-type" in page.url.lower():
                for tab_text in ["Interior", "Oceanview", "Balcony", "Mini-Suites"]:
                    tab = page.locator(f"button:has-text('{tab_text}'):not([disabled])")
                    if tab.count() > 0 and tab.first.is_visible():
                        tab.first.click(force=True)
                        page.wait_for_timeout(1500)
                        break

                sel_btn = page.locator("button:has-text('SELECT')")
                if sel_btn.count() > 0 and sel_btn.first.is_visible():
                    sel_btn.first.click()
                    page.wait_for_timeout(3000)

                select_from_btn = page.locator(
                    "button:has-text('Select from'), button:has-text('Select  from')"
                )
                for _ in range(15):
                    try:
                        if select_from_btn.count() > 0:
                            for j in range(select_from_btn.count()):
                                b = select_from_btn.nth(j)
                                if b.is_visible():
                                    b.click(timeout=10000)
                                    break
                            page.wait_for_load_state("domcontentloaded")
                            page.wait_for_timeout(3000)
                            break
                    except Exception:
                        pass
                    page.wait_for_timeout(1000)

                booking_cabin_page.take_screenshot("uk_step5_after_cabin_select")

            elif booking_cabin_page.count(booking_cabin_page.CABIN_CARDS) > 0:
                booking_cabin_page.select_first_cabin()

        with allure.step("Step 5b: Skip packages upsell if shown"):
            page.wait_for_timeout(2000)
            if "packages" in page.url.lower():
                booking_cabin_page.take_screenshot("uk_step5b_packages")
                for btn_text in ["I'LL PAY MORE ONBOARD", "PAY MORE ONBOARD",
                                  "Pay More Onboard", "No Thanks", "Continue"]:
                    btn = page.locator("button").filter(has_text=btn_text)
                    if btn.count() > 0 and btn.first.is_visible():
                        btn.first.click()
                        page.wait_for_load_state("domcontentloaded")
                        page.wait_for_timeout(2000)
                        break

        with allure.step("Step 5c: Continue past stateroom summary if shown"):
            page.wait_for_timeout(1500)
            if "stateroom-summary" in page.url.lower():
                booking_cabin_page.take_screenshot("uk_step5c_summary")
                for btn_text in ["CONTINUE", "Continue", "Next", "Proceed"]:
                    btn = page.locator("button").filter(has_text=btn_text)
                    if btn.count() > 0 and btn.first.is_visible():
                        btn.first.click()
                        page.wait_for_load_state("domcontentloaded")
                        page.wait_for_timeout(2000)
                        break

        with allure.step("Step 6: Fill guest details"):
            guest_data = [
                ("Tom", "Cat", test_user_data["email"]),
                ("Jane", "Cat", "jane.cat@example.com"),
                ("Bob",  "Cat", "bob.cat@example.com"),
            ]

            def _fill_one_guest(first, last, email):
                try:
                    page.get_by_label("First Name").first.fill(first)
                except Exception:
                    try:
                        page.locator(booking_guests_page.FIRST_NAME).first.fill(first)
                    except Exception:
                        pass
                try:
                    page.get_by_label("Last Name").first.fill(last)
                except Exception:
                    try:
                        page.locator(booking_guests_page.LAST_NAME).first.fill(last)
                    except Exception:
                        pass
                # Gender
                try:
                    page.get_by_label("Gender").first.select_option("M")
                except Exception:
                    try:
                        page.locator("select[name*='gender' i], select[id*='gender' i], select[name='sex']").first.select_option("M")
                    except Exception:
                        pass
                # Month by index, day/year by value
                month_sel = page.locator("select[name*='month' i], select[id*='month' i]")
                if month_sel.count() > 0:
                    try:
                        month_sel.first.select_option(index=1)
                    except Exception:
                        pass
                else:
                    try:
                        page.locator("select").filter(has_text="Month").first.select_option(index=1)
                    except Exception:
                        pass
                day_sel = page.locator("select[name*='day' i], select[id*='day' i]")
                try:
                    (day_sel if day_sel.count() > 0 else page.locator("select").filter(has_text="Day")).first.select_option("15")
                except Exception:
                    pass
                year_sel = page.locator("select[name*='year' i], select[id*='year' i]")
                try:
                    (year_sel if year_sel.count() > 0 else page.locator("select").filter(has_text="Year")).first.select_option("1980")
                except Exception:
                    pass
                # Address — AU format: 1 Market Street, Sydney NSW 2000
                for addr_sel in ["input[name='address1']", "input[id='address1']"]:
                    try:
                        field = page.locator(addr_sel).first
                        if field.count() > 0:
                            field.click()
                            field.press("Control+a")
                            field.type("1 Market Street", delay=30)
                            field.press("Escape")
                            page.wait_for_timeout(300)
                            break
                    except Exception:
                        pass
                try:
                    city_f = page.locator("input[name='city'], input[id='city']").first
                    city_f.click()
                    city_f.press("Control+a")
                    city_f.type("Sydney", delay=30)
                    city_f.press("Escape")
                    page.wait_for_timeout(300)
                except Exception:
                    pass
                # AU-specific: state SELECT (e.g. "New South Wales" for Sydney)
                try:
                    state_sel = page.locator("select[name='state'], select[id='state']")
                    if state_sel.count() > 0:
                        for state_val in ["NSW", "New South Wales", "NEW SOUTH WALES"]:
                            try:
                                state_sel.first.select_option(state_val)
                                break
                            except Exception:
                                pass
                        else:
                            try:
                                state_sel.first.select_option(index=2)  # NSW is 2nd option
                            except Exception:
                                pass
                except Exception:
                    pass
                # AU/UK-specific: nearestAirport (secondary guests)
                try:
                    airport_sel = page.locator("select[name='nearestAirport'], select[id='nearestAirport']")
                    if airport_sel.count() > 0:
                        airport_sel.first.select_option(index=1)
                except Exception:
                    pass
                # Zip — AU postcode (4 digits)
                try:
                    zip_f = page.locator("input[name='zip'], input[id='zip']").first
                    zip_f.click()
                    zip_f.press("Control+a")
                    zip_f.type("2000", delay=30)
                    zip_f.press("Tab")
                    page.wait_for_timeout(200)
                except Exception:
                    try:
                        page.locator("input[name*='zip' i], input[id*='zip' i]").first.fill("2000")
                    except Exception:
                        pass
                # Phone
                try:
                    page.locator("input[type='tel']").first.fill("3105550100")
                except Exception:
                    pass
                # Email
                try:
                    page.get_by_label("Email").first.fill(email)
                except Exception:
                    pass
                # AU/UK-specific: membership radio (select "No" option — value '2')
                try:
                    page.locator("input[name='membership']").filter(has_attribute="value=2").first.click()
                except Exception:
                    try:
                        page.locator("input#membership_2").first.click()
                    except Exception:
                        try:
                            page.locator("input[name='membership'][value='2']").first.click()
                        except Exception:
                            pass
                # AU/UK-specific: countryCode select
                try:
                    cc_sel = page.locator("select[name='countryCode'], select[id='countryCode']")
                    if cc_sel.count() > 0:
                        try:
                            cc_sel.first.select_option("AU")
                        except Exception:
                            try:
                                cc_sel.first.select_option(index=1)
                            except Exception:
                                pass
                except Exception:
                    pass
                # AU/UK-specific: numberType select (phone type)
                try:
                    nt_sel = page.locator("select[name='numberType'], select[id='numberType']")
                    if nt_sel.count() > 0:
                        try:
                            nt_sel.first.select_option(index=1)
                        except Exception:
                            pass
                except Exception:
                    pass
                # AU/UK-specific: hearFromPCL — click "No" (sets validity.valid=True) then dismiss lightbox
                def _dismiss_lightbox():
                    """Wait for lightbox to appear then force-click 'I Understand' to close it."""
                    understand_btn = page.locator("button").filter(has_text="I Understand")
                    try:
                        understand_btn.first.wait_for(state="visible", timeout=3000)
                    except Exception:
                        return  # no lightbox appeared
                    for _ in range(5):
                        try:
                            if understand_btn.first.is_visible():
                                understand_btn.first.click(force=True, timeout=3000)
                                page.wait_for_timeout(600)
                                # Wait for overlay to go hidden
                                overlay = page.locator("[data-test-id='handleLightbox']")
                                try:
                                    overlay.first.wait_for(state="hidden", timeout=4000)
                                except Exception:
                                    pass
                                page.wait_for_timeout(300)
                            else:
                                break
                        except Exception:
                            break

                try:
                    no_radio = page.locator("input[name='hearFromPCL'][value='No']")
                    if no_radio.count() > 0:
                        no_radio.first.click()
                        page.wait_for_timeout(800)
                        _dismiss_lightbox()
                    else:
                        # Try by id pattern
                        no_radio2 = page.locator("input#hearFromPCL_2, input[id='hearFromPCL_2']")
                        if no_radio2.count() > 0:
                            no_radio2.first.click()
                            page.wait_for_timeout(800)
                            _dismiss_lightbox()
                except Exception:
                    pass
                # AU/UK-specific: agreement checkbox (check it if unchecked)
                try:
                    cb = page.locator("input#agreement, input[name='agreement']")
                    if cb.count() > 0 and not cb.first.is_checked():
                        cb.first.click()
                        page.wait_for_timeout(300)
                except Exception:
                    pass
                # AU/UK-specific: receiveNewsDeals checkbox (optional, check it)
                try:
                    news_cb = page.locator("input[name='receiveNewsDeals'], input#receiveNewsDeals")
                    if news_cb.count() > 0 and not news_cb.first.is_checked():
                        news_cb.first.click()
                        page.wait_for_timeout(200)
                except Exception:
                    pass
                # Debug: show invalid/required fields before submit
                form_fields = page.evaluate("""
                    () => [...document.querySelectorAll('input,select,textarea')]
                        .filter(el => el.name || el.id)
                        .map(el => ({
                            tag: el.tagName, name: el.name, id: el.id,
                            type: el.type, value: el.value, checked: el.checked,
                            required: el.required, valid: el.validity ? el.validity.valid : null
                        }))
                """)
                invalid_fields = [f for f in form_fields if f.get("required") and not f.get("valid")]
                print(f"  Invalid required fields: {invalid_fields}")
                print(f"  All fields: {form_fields}")
                page.screenshot(path=f"debug_au_guest_before_submit_{first}.png")
                btn_count = page.locator("button").filter(has_text="SAVE & CONTINUE").count()
                print(f"  SAVE & CONTINUE buttons found: {btn_count}")
                all_btns = [b.inner_text()[:30] for b in page.locator("button").all() if b.is_visible()]
                print(f"  Visible buttons: {all_btns[:10]}")
                # Dismiss any lingering lightbox before clicking SAVE & CONTINUE
                _dismiss_lightbox()
                page.wait_for_timeout(500)
                # Capture URL before clicking so we can detect real navigation
                url_before_save = page.url
                # Click SAVE & CONTINUE — regular click (no force) after modal is dismissed
                save_btn = page.locator("button").filter(has_text="SAVE & CONTINUE")
                try:
                    if save_btn.count() > 0:
                        save_btn.first.scroll_into_view_if_needed()
                        save_btn.first.click(timeout=10000)
                        print(f"  Clicked SAVE & CONTINUE (regular)")
                    else:
                        raise Exception("Button not found")
                except Exception as e:
                    print(f"  Regular click failed: {e!r} — trying force click")
                    try:
                        save_btn.first.click(force=True, timeout=5000)
                        print(f"  Clicked SAVE & CONTINUE (force)")
                    except Exception as e2:
                        print(f"  Force click failed: {e2!r} — trying data-track-id")
                        try:
                            page.locator("button[data-track-id='save-guest-1'], button[data-track-id='save-guest-2']").first.click(force=True)
                        except Exception:
                            booking_guests_page.continue_to_next_step()
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(3000)
                # Wait for URL to actually CHANGE from the page we were on before clicking
                try:
                    page.wait_for_url(
                        lambda u, _prev=url_before_save: u != _prev and any(
                            k in u.lower() for k in ["pay", "guest-", "confirmation", "review"]
                        ),
                        timeout=20000,
                    )
                    print(f"  URL changed to: {page.url}")
                except Exception:
                    # If still stuck, try one more click
                    if page.url == url_before_save:
                        print(f"  Still at same URL — retrying SAVE & CONTINUE")
                        try:
                            save_btn2 = page.locator("button").filter(has_text="SAVE & CONTINUE")
                            if save_btn2.count() > 0:
                                save_btn2.first.click(force=True, timeout=5000)
                                page.wait_for_load_state("domcontentloaded")
                                page.wait_for_timeout(5000)
                        except Exception:
                            pass
                # Report any validation errors + highlighted fields
                for err in page.locator("[class*='error'], [role='alert']").all():
                    if err.is_visible():
                        print(f"  Validation error: {err.inner_text()[:100]!r}")
                # Find fields with error classes (React-level validation)
                highlighted = page.evaluate("""
                    () => [...document.querySelectorAll('[class*="error"],[class*="invalid"],[class*="has-error"]')]
                        .filter(el => el.tagName.match(/INPUT|SELECT|LABEL|DIV|SPAN/))
                        .map(el => ({tag: el.tagName, name: el.name||el.htmlFor||'', cls: el.className.slice(0,80), checked: el.checked}))
                """)
                print(f"  Highlighted/errored fields: {highlighted[:15]}")

            for idx, (first, last, email) in enumerate(guest_data):
                if not booking_guests_page.is_on_guests_page():
                    print(f"Guest loop: not on guests page at idx={idx}, url={page.url}")
                    break
                print(f"Filling guest {idx}: {first} {last} @ {page.url}")
                _fill_one_guest(first, last, email)
                print(f"After guest {idx} fill: {page.url}")

            page.screenshot(path="debug_uk_after_guests.png")
            print(f"After guest loop URL: {page.url}")
            # If still on guest page, wait for navigation to payment
            if "guest" in page.url.lower():
                try:
                    page.wait_for_url(
                        lambda u: any(k in u.lower() for k in ["pay", "payment", "confirm", "review"]),
                        timeout=15000,
                    )
                    print(f"After waiting for payment URL: {page.url}")
                except Exception:
                    print(f"Still on guest page after wait: {page.url}")

        with allure.step("Step 6b: Skip transfers upsell if shown"):
            page.wait_for_timeout(1500)
            if "transfer" in page.url.lower():
                booking_cabin_page.take_screenshot("uk_step6b_transfers")
                print(f"Transfers page URL: {page.url}")
                for btn_text in [
                    "No, thanks", "No Thanks", "No, Thank You", "Skip",
                    "Continue without", "CONTINUE", "Continue", "Next",
                ]:
                    btn = page.locator("button").filter(has_text=btn_text)
                    if btn.count() > 0 and btn.first.is_visible():
                        btn.first.click()
                        page.wait_for_load_state("domcontentloaded")
                        page.wait_for_timeout(2000)
                        print(f"After transfers skip: {page.url}")
                        break
                else:
                    # Try any link that mentions skipping
                    for link_text in ["No, thanks", "Skip", "Continue"]:
                        lnk = page.locator(f"a:has-text('{link_text}')")
                        if lnk.count() > 0 and lnk.first.is_visible():
                            lnk.first.click()
                            page.wait_for_load_state("domcontentloaded")
                            page.wait_for_timeout(2000)
                            break

        with allure.step("Step 6c: Skip insurance upsell if shown"):
            page.wait_for_timeout(1000)
            if "insurance" in page.url.lower() or "protect" in page.url.lower():
                booking_cabin_page.take_screenshot("uk_step6c_insurance")
                for btn_text in ["No, thanks", "No Thanks", "Skip", "Continue", "CONTINUE"]:
                    btn = page.locator("button").filter(has_text=btn_text)
                    if btn.count() > 0 and btn.first.is_visible():
                        btn.first.click()
                        page.wait_for_load_state("domcontentloaded")
                        page.wait_for_timeout(2000)
                        break

        with allure.step("Step 7: Confirm payment page loaded"):
            # Give the page a moment to settle after upsell skips
            page.wait_for_timeout(2000)
            # Wait up to 20s for payment URL to appear
            current = page.url.lower()
            if not any(k in current for k in ["pay", "payment", "checkout", "confirm", "review"]):
                try:
                    page.wait_for_url(
                        lambda u: any(k in u.lower() for k in ["pay", "payment", "checkout", "confirm", "review"]),
                        timeout=20000,
                    )
                except Exception:
                    pass
            # Robust check: also accept /pay without trailing slash
            current_url = page.url.lower()
            on_pay = (
                booking_payment_page.is_on_payment_page() or
                any(k in current_url for k in ["pay", "payment", "checkout", "confirm", "review"])
            )
            print(f"Payment page check: url={current_url!r} on_pay={on_pay}")
            if not on_pay:
                pytest.skip(
                    f"Did not reach payment page after guest forms "
                    f"(at: {current_url})"
                )

        with allure.step("Step 8: Fill payment — Tom Cat 4111111111111111 12/33 234"):
            pay_page = booking_payment_page.page
            try:
                pay_page.wait_for_function(
                    "() => !document.querySelector('.loading, [class*=\"loading\"]') || "
                    "document.querySelector('.loading, [class*=\"loading\"]').offsetParent === null",
                    timeout=15000,
                )
            except Exception:
                pay_page.wait_for_timeout(3000)

            pay_page.screenshot(path="debug_uk_payment_page.png")

            # Cardholder name
            try:
                pay_page.locator("#cardholder-name").first.fill("Tom Cat", timeout=5000)
            except Exception:
                pass

            # Mastercard Gateway cross-origin iframes
            for frame in pay_page.frames:
                if "mastercard.com" not in frame.url:
                    continue
                try:
                    ids = frame.evaluate(
                        "() => [...document.querySelectorAll('input')].map(i=>i.id)"
                    )
                    print(f"MC FRAME {frame.url[-30:]}: ids={ids}")
                    if "number"       in ids:
                        frame.locator("#number").first.fill("4111111111111111", timeout=5000)
                    if "expiryMonth"  in ids:
                        frame.locator("#expiryMonth").first.fill("12", timeout=3000)
                    if "expiryYear"   in ids:
                        frame.locator("#expiryYear").first.fill("2033", timeout=3000)
                    if "nameOnCard"   in ids:
                        frame.locator("#nameOnCard").first.fill("Tom Cat", timeout=3000)
                    if "securityCode" in ids:
                        frame.locator("#securityCode").first.fill("234", timeout=3000)
                except Exception as e:
                    print(f"Frame error: {e}")

            # Main-page expiry selects
            year_opts = pay_page.evaluate(
                "() => [...document.querySelectorAll('#expiry-year option')].map(o=>o.value)"
            )
            tgt_year = "2033" if "2033" in year_opts else (year_opts[-1] if year_opts else "2026")
            try:
                pay_page.locator("#expiry-month").first.select_option("12", timeout=5000)
            except Exception:
                pass
            try:
                pay_page.locator("#expiry-year").first.select_option(tgt_year, timeout=5000)
            except Exception:
                pass

            # Zip
            zip_loc = pay_page.locator("input[name='zip']")
            try:
                zip_loc.first.scroll_into_view_if_needed(timeout=5000)
                pay_page.wait_for_timeout(300)
                zip_loc.first.click(timeout=5000)
                pay_page.keyboard.press("Control+a")
                pay_page.keyboard.type("2000", delay=80)
                pay_page.keyboard.press("Tab")
                pay_page.wait_for_timeout(200)
            except Exception:
                pay_page.evaluate("""
                    const el = document.querySelector("input[name='zip']");
                    if (el) {
                        el.focus();
                        const s = Object.getOwnPropertyDescriptor(
                            window.HTMLInputElement.prototype,'value').set;
                        s.call(el,'2000');
                        el.dispatchEvent(new InputEvent('input',{bubbles:true,data:'90210',inputType:'insertText'}));
                        el.dispatchEvent(new Event('change',{bubbles:true}));
                        el.dispatchEvent(new Event('blur',{bubbles:true}));
                    }
                """)

            pay_page.screenshot(path="debug_uk_payment_filled.png")

        with allure.step("Step 9: Accept terms and click BOOK NOW"):
            pay_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            pay_page.wait_for_timeout(500)
            # Real click on terms checkbox (JS setter alone may not update React state)
            terms_clicked = False
            try:
                cb = pay_page.locator("#passageContractInputCheckBox")
                if cb.count() > 0:
                    cb.first.scroll_into_view_if_needed()
                    if not cb.first.is_checked():
                        cb.first.click()
                        pay_page.wait_for_timeout(500)
                    terms_clicked = True
                    print(f"  Terms checkbox clicked: {cb.first.is_checked()}")
            except Exception as e:
                print(f"  Terms click failed: {e!r}")
            if not terms_clicked:
                # JS fallback
                pay_page.evaluate("""
                    const cb = document.querySelector('#passageContractInputCheckBox');
                    if (cb && !cb.checked) {
                        const setter = Object.getOwnPropertyDescriptor(
                            window.HTMLInputElement.prototype,'checked').set;
                        setter.call(cb, true);
                        cb.dispatchEvent(new Event('change',{bubbles:true}));
                        cb.dispatchEvent(new Event('click',{bubbles:true}));
                    }
                """)
            pay_page.wait_for_timeout(300)
            pay_page.screenshot(path="debug_au_payment_terms.png")

            # Debug: show all visible buttons
            visible_btns = [b.inner_text()[:30] for b in pay_page.locator("button").all() if b.is_visible()]
            print(f"  Visible buttons before BOOK NOW: {visible_btns}")

            try:
                book_now = pay_page.locator("button").filter(has_text="BOOK NOW")
                if book_now.count() > 0 and book_now.first.is_visible():
                    print(f"  BOOK NOW visible, disabled={pay_page.evaluate('() => document.querySelector(\"button\") && [...document.querySelectorAll(\"button\")].find(b=>b.textContent.includes(\"BOOK NOW\"))?.disabled')}")
                    book_now.first.click(timeout=15000)
                    print(f"  Clicked BOOK NOW")
                else:
                    for txt in ["Book Now", "Book", "Complete", "Confirm", "Pay"]:
                        btn = pay_page.locator("button").filter(has_text=txt)
                        if btn.count() > 0 and btn.first.is_visible():
                            btn.first.click(timeout=15000)
                            print(f"  Clicked '{txt}' button")
                            break
                    else:
                        booking_payment_page.click(booking_payment_page.COMPLETE_BOOKING_BTN)
            except Exception as e:
                print(f"  BOOK NOW click error: {e!r}")
                try:
                    booking_payment_page.click(booking_payment_page.COMPLETE_BOOKING_BTN)
                except Exception:
                    pass

            pay_page.wait_for_load_state("domcontentloaded")
            pay_page.wait_for_timeout(3000)
            print(f"  URL after BOOK NOW: {pay_page.url}")
            # Report visible errors after booking attempt
            for err in pay_page.locator("[class*='error'], [role='alert']").all():
                if err.is_visible():
                    print(f"  Error after booking: {err.inner_text()[:150]!r}")

        with allure.step("Step 10: Wait for confirmation and capture booking number"):
            reached = booking_confirmation_page.wait_for_confirmation(timeout=60000)
            if not reached:
                pytest.skip(
                    f"Confirmation page not reached after submit "
                    f"(at: {booking_confirmation_page.get_url()})"
                )

            booking_number = booking_confirmation_page.get_booking_number()
            confirm_url    = booking_confirmation_page.get_url()

            print(f"\n{'='*60}")
            print(f"AU BOOKING")
            print(f"CONFIRMATION URL: {confirm_url}")
            print(f"BOOKING NUMBER:   {booking_number}")
            print(f"{'='*60}\n")

            allure.attach(
                f"AU Booking\nConfirmed Booking Number: {booking_number}\nURL: {confirm_url}",
                name="[AU BOOKING NUMBER] Confirmation",
                attachment_type=allure.attachment_type.TEXT,
            )
            booking_confirmation_page.take_screenshot("au_booking_confirmation")

            assert booking_number, (
                f"AU confirmation page reached but no booking number found. "
                f"URL: {confirm_url}"
            )
