# test_simple_app.py
import pytest
import tkinter as tk
from gallery_wall_planner.main import SimpleApp

# Fixture to set up the Tkinter root and app instance for tests
@pytest.fixture
def app():
    root = tk.Tk()
    # Prevent the window from actually appearing during tests
    # root.withdraw() # Option 1: Hide the window
    # Alternative: Speed up tests by disabling mainloop graphical updates entirely
    # This is often faster but less 'realistic' if testing visual layout precisely
    root.update_idletasks() # Process initial layout
    # For many tests, you might not even need the root window fully initialized graphically

    app_instance = SimpleApp(root)

    # Yield the app instance to the tests
    yield app_instance

    # Teardown: Destroy the root window after the test runs
    # Add error handling in case the window was already destroyed
    try:
        if root.winfo_exists():
             root.destroy()
    except tk.TclError:
        pass # Ignore errors if window is already gone

# --- Your Pytest Tests ---

def test_initial_label_value(app):
    """Test if the label has the correct initial value."""
    assert app.label.cget("text") == "Initial Value"
    # Or using the variable
    assert app.label_var.get() == "Initial Value"

def test_update_label_with_text(app):
    """Test updating the label text via the entry and button."""
    test_input = "Hello Tkinter"

    # 1. Simulate typing into the entry widget
    app.entry.insert(0, test_input)
    assert app.entry.get() == test_input # Verify entry content immediately

    # 2. Simulate clicking the button
    app.button.invoke()

    # 3. **** CRITICAL: Process Tkinter events so the label updates ****
    #    Use update_idletasks() for processing redraws/variable traces
    #    Use update() if invoke() might trigger other event bindings you need processed
    app.root.update_idletasks()
    # app.root.update() # Use if update_idletasks doesn't suffice

    # 4. Assert the label text has changed
    expected_text = f"Updated to: {test_input}"
    assert app.label_var.get() == expected_text
    # You can also check the widget directly, though checking the var is often better
    assert app.label.cget("text") == expected_text

def test_update_label_with_empty_entry(app):
    """Test clicking the button when the entry is empty."""
    assert app.entry.get() == "" # Ensure entry is empty initially

    # Simulate clicking the button
    app.button.invoke()

    # Process events
    app.root.update_idletasks()

    # Assert the label shows the 'empty' message
    assert app.label_var.get() == "Entry was empty!"
    assert app.label.cget("text") == "Entry was empty!"

# To run these tests:
# 1. Make sure you have pytest installed: pip install pytest
# 2. Save the app code as simple_app.py
# 3. Save the test code as test_simple_app.py
# 4. Run pytest in your terminal in the same directory: pytest