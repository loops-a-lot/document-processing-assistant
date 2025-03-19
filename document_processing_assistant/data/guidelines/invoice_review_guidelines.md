# Invoice Data Review Guidelines

## General Guidelines

- Verify all required fields are present and correctly extracted
- Ensure numeric values have proper decimal precision
- Validate dates are in the correct format (YYYY-MM-DD)
- Check that calculations follow the rules specified in the JSON data

## Field-Specific Guidelines

### Invoice Number
- Must follow format INV-YYYY-XXXX
- Year portion should match the invoice date year
- Each invoice number should be unique

### Invoice Date
- Must be a valid date in YYYY-MM-DD format
- Should not be in the future
- Should be within the last 90 days

### Due Date
- Must be after invoice date
- Typically follows payment terms (Net 30 = invoice date + 30 days)

### Customer Information
- Verify customer name matches the company letterhead
- Customer ID should match our records
- Look for any special notes or requirements for specific customers

### Amount Fields
- Subtotal: Sum of all line items before tax
- Tax Rate: Verify correct rate was applied based on customer location
- Tax Amount: Must equal Subtotal × Tax Rate
- Total Amount: Must equal Subtotal + Tax Amount

### Currency
- Must be a valid 3-letter currency code
- Should match the currency symbol shown on the invoice

## Validation Process

1. Review the extracted data against the visible text in the invoice
2. Check that calculated fields follow their formulas
3. Verify formatting rules are followed
4. Make corrections when needed and document the changes
5. Save the updated data

## Common Issues

- OCR might misread similar characters (0/O, 1/I, 5/S)
- Handwritten notes might be included in extracted text
- Table structures can cause confusion in data extraction
- Multiple pages may contain redundant information

## Submit for Verification

After completing your review, if you are unsure about any changes:
1. Add detailed notes explaining your uncertainty
2. Flag the record for secondary review
3. Proceed to the next document