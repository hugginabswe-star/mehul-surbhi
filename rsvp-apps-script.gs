const SHEET_ID = "1FBe3RwCyFhiRxjprhDWHeEdbpz4lHJr2clD2G5OY8l0";   // hugginab.swe@gmail.com
// RSVP receiver for https://hugginabswe-star.github.io/mehul-surbhi/
// Lives in the "Wedding RSVP — Mehul & Surbhi" Google Sheet (mehulspatel.mp) → Extensions → Apps Script.
const HEAD = ["Time","Name","Mobile","Attending","Guests","Functions","Message","Invite","Lang"];

function setup() {            // run once: writes headers and asks for permission
  const sh = SpreadsheetApp.openById(SHEET_ID).getSheets()[0];
  if (sh.getLastRow() === 0) { sh.appendRow(HEAD); sh.setFrozenRows(1); sh.getRange(1,1,1,HEAD.length).setFontWeight("bold"); }
  MailApp.getRemainingDailyQuota();
}

function doPost(e) {
  const lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    const p = e.parameter;
    const sh = SpreadsheetApp.openById(SHEET_ID).getSheets()[0];
    if (sh.getLastRow() === 0) sh.appendRow(HEAD);
    sh.appendRow([new Date(), p.name, "'" + (p.phone||""), p.attending, Number(p.guests||0), p.events, p.message, p.invite, p.lang]);
    const to = Session.getEffectiveUser().getEmail();
    MailApp.sendEmail(to, "RSVP: " + p.name + " — " + p.attending + " (" + p.guests + ")",
      ["Name: "+p.name,"Mobile: "+p.phone,"Attending: "+p.attending,"Guests: "+p.guests,"Functions: "+p.events,"Message: "+(p.message||"")].join("\n"));
  } finally { lock.releaseLock(); }
  return ContentService.createTextOutput("ok");
}
