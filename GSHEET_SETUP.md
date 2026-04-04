# MEPCalc Tool Request Form — Google Sheets Integration

## How It Works
1. User fills out the "Need a Custom Tool?" form on index.html
2. Form POSTs JSON to a Google Apps Script web app
3. Apps Script appends a row to your Google Sheet
4. You review submissions in the spreadsheet at your own pace

## Setup (5 minutes, one time)

### Step 1: Create the Google Sheet
1. Go to [sheets.google.com](https://sheets.google.com) and create a new spreadsheet
2. Name it "MEPCalc Tool Requests" (or whatever you prefer)
3. In Row 1, add these headers:
   - A1: `Timestamp`
   - B1: `Name`
   - C1: `Email`
   - D1: `Company`
   - E1: `Role`
   - F1: `Description`
   - G1: `Source`

### Step 2: Add the Apps Script
1. In the spreadsheet, go to **Extensions → Apps Script**
2. Delete any existing code in `Code.gs`
3. Paste the code below
4. Click **Save** (disk icon)

```javascript
function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var data;

  try {
    data = JSON.parse(e.postData.contents);
  } catch (err) {
    return ContentService.createTextOutput(
      JSON.stringify({ status: 'error', message: 'Invalid JSON' })
    ).setMimeType(ContentService.MimeType.JSON);
  }

  sheet.appendRow([
    data.timestamp || new Date().toISOString(),
    data.name || '',
    data.email || '',
    data.company || '',
    data.role || '',
    data.description || '',
    data.source || 'MEPCalc',
  ]);

  return ContentService.createTextOutput(
    JSON.stringify({ status: 'ok' })
  ).setMimeType(ContentService.MimeType.JSON);
}
```

### Step 3: Deploy as Web App
1. In Apps Script, click **Deploy → New deployment**
2. Click the gear icon next to "Select type" and choose **Web app**
3. Settings:
   - Description: `MEPCalc form handler`
   - Execute as: **Me** (your Google account)
   - Who has access: **Anyone**
4. Click **Deploy**
5. Copy the **Web app URL** (looks like `https://script.google.com/macros/s/AKfyc.../exec`)

### Step 4: Add the URL to MEPCalc
1. Open `index.html`
2. Find this line near the top of the script block:
   ```javascript
   const GSHEET_WEBHOOK = '';
   ```
3. Paste your web app URL between the quotes:
   ```javascript
   const GSHEET_WEBHOOK = 'https://script.google.com/macros/s/AKfyc.../exec';
   ```
4. Save. Done.

## How It Behaves

- **With webhook configured:** Form submits to Google Sheet + saves to localStorage as backup
- **Without webhook (current state):** Form saves to localStorage only, shows "Request saved!" message
- **If network fails:** Falls back to localStorage, shows "Saved locally" in orange
- **Validation:** Requires name, valid email, and description before submitting

## Reviewing Submissions
- Open the Google Sheet anytime — all requests are there with timestamps
- Sort by date, filter by company, add your own status columns
- No notifications are sent automatically — check the sheet on your own schedule
- To add email notifications: In Apps Script, add `MailApp.sendEmail(...)` inside `doPost()`

## Optional: Email Notification on New Submission

Add this inside the `doPost` function, after `sheet.appendRow(...)`:

```javascript
MailApp.sendEmail({
  to: 'your-email@gmail.com',
  subject: 'New MEPCalc Tool Request from ' + (data.name || 'Unknown'),
  body: 'Name: ' + data.name + '\n'
      + 'Email: ' + data.email + '\n'
      + 'Company: ' + data.company + '\n'
      + 'Role: ' + data.role + '\n\n'
      + 'Request:\n' + data.description
});
```
