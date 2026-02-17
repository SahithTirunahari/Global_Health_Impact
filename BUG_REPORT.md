# Bug Report

## Bug 1: Login Credentials Persistence
**What's broken:** The login form was pre-populating with test credentials even after logging out, and browser autocomplete was enabled.
**Where:** `templates/login.html` 
**Why it matters:** Security risk. Public or shared computers would expose user credentials. It also confuses users who expect a fresh login state after logging out.
**How I fixed it:** Removed the hardcoded `value` attributes from the email and password input fields and added `autocomplete="off"` to the form tag.
**How to test:**
1. Log in to the application.
2. Click "Logout".
3. Verify that the email and password fields are empty.

## Bug 2: Search Matching Logic
**What's broken:** The search functionality was matching files if the query string appeared *anywhere* in the filename, rather than just at the beginning.
**Where:** `app.py` 
**Why it matters:** Functionality issue.
**How I fixed it:** Changed the filter logic from `if query in f['name'].lower()` to `if f['name'].lower().startswith(query)`.
**How to test:**
1. Go to the dashboard.
2. Search for "re" (should match "research_paper.pdf").
3. Search for "paper" (should NOT match "research_paper.pdf").

## Bug 3: Insecure and Fake File Upload
**What's broken:** The upload feature was a "dummy" implementation. It took a text string as a filename, didn't actually upload a file, and had no validation other than checking for a dot in the string.
**Where:** `app.py` and `templates/dashboard.html` 
**Why it matters:** **Critical Security Risk.** An attacker could "upload" a file named `malware.exe.pdf`. It also lacked actual functionality users couldn't upload real files.
**How I fixed it:**
1. Updated `dashboard.html` to use `<input type="file">` and `enctype="multipart/form-data"`.
2. Updated `app.py` to use `request.files`, validate the file extension against a safe list, and save the file to a local `uploads/` directory.
**How to test:**
1. Try to upload a file with an invalid extension (e.g., `.exe`). It should fail.
2. Upload a valid file (e.g., `.pdf` or `.txt`).
3. Verify the file appears in the list and exists in the `uploads/` folder.

## Bug 4: Unprotected Dashboard Route
**What's broken:** The `/dashboard` route had no check to see if the user was logged in.
**Where:** `app.py` 
**Why it matters:** **Security Vulnerability.** Anyone could access the dashboard by navigating directly to `/dashboard` without logging in. It would also cause a server crash (500 error) because `session.get('email')` would be `None`.
**How I fixed it:** Added a check at the beginning of the `dashboard` function: `if 'email' not in session: return redirect(url_for('login'))`.
**How to test:**
1. Logout.
2. Try to manually navigate to `http://localhost:5000/dashboard`.
3. You should be redirected to the login page.

## Bug 5: N+1 Query Performance Issue
**What's broken:** The API endpoint `/api/files` was iterating through every file and performing a user lookup for each one.
**Where:** `app.py` 
**Why it matters:** **Performance.** In a real application with a database, this would execute N+1 database queries (where N is the number of files), causing extreme slowness as the dataset grows.
**How I fixed it:** Refactored the code to fetch the current user *once* and then simply filter the file list.
**How to test:**
1. Access `http://localhost:5000/api/files` while logged in.
2. The response should be the same JSON as before, but the backend is now more efficient.
