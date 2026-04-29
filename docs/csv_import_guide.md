# CSV Import Guide for Students

This guide explains how to use the bulk CSV import feature to add multiple students to Skola at once.

## Accessing the Import Feature

1. Log in as an **Administrator**
2. Navigate to **Students** from the main menu
3. Click the **Import CSV** button in the top right corner

## CSV File Format

Your CSV file must include the following columns (column names must match exactly):

### Required Columns:
- `admission_number` - Unique identifier for the student (e.g., ST2026001)
- `first_name` - Student's first name
- `last_name` - Student's last name  
- `date_of_birth` - Birth date in **YYYY-MM-DD** format (e.g., 2010-03-15)
- `guardian_name` - Full name of parent/guardian

### Optional Columns:
- `contact_email` - Guardian's email address
- `contact_phone` - Guardian's phone number
- `status` - Student status: ACTIVE, INACTIVE, or GRADUATED (defaults to ACTIVE)

## Sample CSV Format

```csv
admission_number,first_name,last_name,date_of_birth,guardian_name,contact_email,contact_phone,status
ST2026001,John,Smith,2010-03-15,Robert Smith,robert.smith@example.com,555-0101,ACTIVE
ST2026002,Emma,Johnson,2011-07-22,Sarah Johnson,sarah.j@example.com,555-0102,ACTIVE
ST2026003,Michael,Williams,2010-11-08,David Williams,d.williams@example.com,555-0103,ACTIVE
```

A sample file is included in the project root: `students_import_sample.csv`

## Import Process

### Step 1: Upload CSV File
1. Click **Choose File** and select your CSV file
2. Click **Preview Import**

### Step 2: Review Preview
The system will:
- Validate all data
- Check for duplicate admission numbers
- Verify date formats
- Display any errors found

You'll see:
- ✅ **Green box**: Number of valid students ready to import
- ❌ **Red box**: List of errors (if any)
- **Table preview**: Shows the students that will be imported

### Step 3: Confirm Import
- If there are **no errors**: Click **Confirm & Import** to add the students
- If there are **errors**: Click **Try Again**, fix the CSV file, and re-upload

## Common Errors and Solutions

| Error | Solution |
|-------|----------|
| Missing required columns | Ensure CSV has all required column headers spelled correctly |
| Duplicate admission_number | Each admission number must be unique; check for duplicates in your file |
| Invalid date format | Use YYYY-MM-DD format (e.g., 2010-03-15, not 03/15/2010) |
| File too large | CSV file must be under 5MB |
| Invalid status | Use only ACTIVE, INACTIVE, or GRADUATED |

## Exporting Student Data

You can also **export** existing student data to CSV:

1. Navigate to **Students** 
2. Click **Export CSV** button
3. A CSV file will download with all current student records
4. Use this exported file as a template for future imports

## Tips

- **Create a template**: Export current students to get a properly formatted CSV template
- **Test with small files first**: Try importing 2-3 students to test your CSV format
- **Keep backups**: Save a copy of your CSV file before importing
- **Verify data**: Always review the preview before confirming the import
- **Check admission numbers**: Ensure they follow your school's numbering system

## Permissions

Only users with **Administrator** role can access import/export features. If you don't see the Import/Export buttons, contact your system administrator.

## Need Help?

If you encounter issues:
1. Check that your CSV file matches the required format
2. Verify all dates are in YYYY-MM-DD format
3. Ensure admission numbers are unique
4. Contact your system administrator for assistance
