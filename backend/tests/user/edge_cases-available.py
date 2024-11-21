# Test 2: Attempt to Book a Room in the Past
    def test_book_room_in_past():
        page.goto("http://localhost:5000/user/dashboard")
        current_time = datetime.datetime.now()
        past_time = (current_time - datetime.timedelta(hours=1)).strftime("%H:%M")
        
        page.evaluate(f"""
            () => {{
                const selectInfo = {{
                    startStr: '{current_time.strftime("%Y-%m-%d")}T{past_time}:00',
                    endStr: '{current_time.strftime("%Y-%m-%d")}T{current_time.strftime("%H:%M")}:00',
                    allDay: false
                }};
                if (typeof openBookingModal === 'function') {{
                    openBookingModal(selectInfo);
                }}
            }}
        """)
        page.get_by_role("button", name="Book Room").click()
        error_message = page.locator(".error-message")
        expect(error_message).to_be_visible()
        expect(error_message).to_have_text("Start time cannot be in the past")
        
# Test 3: Attempt to Book Overlapping Time Slots
    def test_book_overlapping_slots():
        # Assuming a room is already booked for tomorrow 3-4 PM
        page.goto("http://localhost:5000/dashboard")
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        page.evaluate(f"""
            () => {{
                const selectInfo = {{
                    startStr: '{tomorrow}T15:30:00',
                    endStr: '{tomorrow}T16:30:00',
                    allDay: false
                }};
                if (typeof openBookingModal === 'function') {{
                    openBookingModal(selectInfo);
                }}
            }}
        """)
        page.get_by_role("textbox", name="test1").click()
        page.get_by_role("option", name="Room C").click()
        page.get_by_role("button", name="Book Room").click()
        error_message = page.locator(".error-message")
        expect(error_message).to_be_visible()
        expect(error_message).to_have_text("This time slot overlaps with an existing booking")
        
# Test 5: Attempt to Book All Rooms and Then Try to Book Another
    def test_book_all_rooms():
        # Assuming user is logged in and all rooms are available
        page.goto("http://localhost:5000/user/dashboard")
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Book all available rooms
        available_rooms = page.locator(".room-toggle")
        for i in range(available_rooms.count()):
            page.evaluate(f"""
                () => {{
                    const selectInfo = {{
                        startStr: '{tomorrow}T{15+i}:00:00',
                        endStr: '{tomorrow}T{16+i}:00:00',
                        allDay: false
                    }};
                    if (typeof openBookingModal === 'function') {{
                        openBookingModal(selectInfo);
                    }}
                }}
            """)
            page.get_by_role("textbox", name="test1").click()
            page.get_by_role("option").nth(0).click()
            page.get_by_role("button", name="Book Room").click()
            page.get_by_role("button", name="Yes, book it!").click()
            page.locator("button.swal2-confirm").click()

        # Try to book another room
        page.evaluate(f"""
            () => {{
                const selectInfo = {{
                    startStr: '{tomorrow}T20:00:00',
                    endStr: '{tomorrow}T21:00:00',
                    allDay: false
                }};
                if (typeof openBookingModal === 'function') {{
                    openBookingModal(selectInfo);
                }}
            }}
        """)
        no_rooms_message = page.locator("#roomSelect option")
        expect(no_rooms_message).to_have_text("No rooms available")