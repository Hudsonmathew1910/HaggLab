# Northwind Supplies — Office Procedures (SOPs)

Fictional sample company · For demonstration only. DeskPilot uses these procedures to plan computer tasks. It never deletes files.

## SOP-01 Naming and filing supplier invoices
1. Supplier invoices arrive as PDF attachments in the shared inbox accounts@northwind.example.
2. Save each PDF to `Finance/Invoices/Inbox`.
3. Rename each file as `YYYY-MM-DD_Supplier_InvoiceNumber.pdf`, using the invoice date, e.g. `2026-09-14_Acme_INV-2231.pdf`.
4. Move renamed files to `Finance/Invoices/YYYY/MM`, by invoice date. Create the month folder if it does not exist.
5. Add a row to `Finance/Invoices/invoice_register.xlsx`: date, supplier, invoice number, amount, due date.
6. Never delete the original email. Never overwrite an existing file; if the name already exists, add `_2` to the end.

## SOP-02 Weekly sales report
1. Every Monday by 10:00, export last week's sales from the till system to `Reports/Sales/Raw` as CSV.
2. Open `Reports/Sales/weekly_template.xlsx` and paste the data into the Data sheet.
3. Save as `Reports/Sales/Weekly/Sales_Week_YYYY-WW.xlsx`.
4. Email the file to the sales-managers list with the subject `Weekly sales — week WW`.

## SOP-03 Filing customer contracts
1. Signed contracts arrive as PDF.
2. Rename as `Customer_ContractType_StartDate.pdf`, e.g. `Brightcart_ServiceAgreement_2026-10-01.pdf`.
3. Move to `Legal/Contracts/Active`.
4. Copy the start date, end date and renewal notice period into `Legal/contract_register.xlsx`.
5. Contracts that have ended move to `Legal/Contracts/Archive`. Never delete contracts.

## SOP-04 New employee setup folder
1. Create a folder `HR/Employees/Surname_FirstName` (fictional names only in examples).
2. Inside it create three folders: `Contract`, `ID documents`, `Reviews`.
3. Copy `HR/Templates/Welcome_Checklist.docx` into the new folder.
4. Draft a welcome email to the new employee using the template in `HR/Templates/welcome_email.txt`.

## SOP-05 Monthly expense claims
1. Expense claims arrive as PDF or image receipts in `Finance/Expenses/Inbox`.
2. Rename each file as `YYYY-MM_EmployeeID_Amount.pdf`.
3. Move to `Finance/Expenses/YYYY-MM`.
4. Build `Finance/Expenses/YYYY-MM/summary.xlsx` listing employee ID, amount and category for each file.

## SOP-06 Meeting notes
1. Save meeting notes as `Meetings/YYYY/YYYY-MM-DD_Topic.docx`.
2. Draft a follow-up email with the action points to everyone who attended.

## SOP-07 Backups and clean-up
1. Each Friday, copy the `Finance` and `Legal` folders to the `Backup/YYYY-MM-DD` folder on the shared drive.
2. Old files are archived, not deleted: move files older than 2 years from `Inbox` folders to the matching `Archive` folder.
3. Only the IT team may delete files, and only after written approval from the department head.

## Safety rules for any automated tool
- Allowed actions: list files, read files, rename, move, copy, create folders, create spreadsheets, draft emails.
- Ask the user before any rename, move, overwrite or email send, and show the list of changes first.
- Never delete files. Never send an email without the user pressing Send.
- Keep a log of every action: time, file, old name, new name or new location.
- Every rename or move must be reversible from the log.
