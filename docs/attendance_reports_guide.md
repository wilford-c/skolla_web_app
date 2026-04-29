# Attendance Reports & Analytics Guide

This guide explains how to use the attendance reporting and analytics features in Skola.

## Accessing Reports

1. Navigate to **Attendance** from the main menu
2. Click **View Reports** button
   - OR directly access via: `/attendance/reports/`

**Permissions**: Available to Administrators, Staff, and Teachers

## Features Overview

### 1. Interactive Filtering

Filter reports by multiple criteria:
- **Date Range**: Select start and end dates (defaults to last 30 days)
- **Classroom**: Filter by specific class
- **Subject**: Filter by specific subject
- **Student**: View data for individual students
- **Status**: Filter by attendance status (Present, Absent, Late, Excused)

### 2. Statistics Summary

The dashboard displays key metrics:
- **Present Count**: Total present records with percentage
- **Absent Count**: Total absent records with percentage  
- **Late Count**: Total late arrivals with percentage
- **Excused Count**: Total excused absences with percentage

Color-coded cards make it easy to identify trends at a glance.

### 3. Visual Charts

Two interactive charts powered by Chart.js:

#### Daily Attendance Trends (Line Chart)
- Shows daily breakdown of all attendance statuses
- Helps identify patterns over time
- Interactive tooltips show exact numbers

#### Status Distribution (Doughnut Chart)
- Pie chart showing overall distribution
- Visual representation of attendance patterns
- Percentage breakdown by status

### 4. Students with Most Absences

A table displaying the top 10 students with the most absences or late arrivals:
- Shows admission number and full name
- Displays total absence count
- Helps identify students who may need intervention

### 5. Recent Records Table

Displays the latest 100 attendance records matching your filters:
- Date, student name, classroom, subject, status
- Quickly review detailed records
- Supports all filter criteria

## Exporting Reports

### CSV Export

Export detailed records to CSV format:

1. Apply your desired filters
2. Click **Export CSV** button
3. File downloads automatically as `attendance_report.csv`

**CSV Contents**:
- Date
- Student ID and Name
- Classroom and Subject
- Status
- Notes
- Recorded By (user who logged it)
- Timestamp

**Use Cases**:
- Import into Excel/Google Sheets for further analysis
- Share with administrators or external stakeholders
- Create custom reports using pivot tables

### PDF Export

Generate a summary report as PDF:

1. Apply your desired filters  
2. Click **Export PDF** button
3. File downloads as `attendance_report.pdf`

**PDF Contents**:
- Report header with date range
- Total record count
- Statistics table with counts and percentages
- Professional formatting suitable for printing

**Requirements**: PDF export requires the `reportlab` library. If not installed, you'll see an error message with installation instructions:
```bash
pip install reportlab
```

## Dashboard Widget

The main dashboard shows an **Attendance Overview** widget (last 7 days):
- Present, Absent, and Late counts
- Total records
- Quick link to full reports
- Only visible to Admin/Staff users

## Guardian Daily Digest Emails

Guardians who set notification mode to **Daily Digest** receive one attendance summary email per day for qualifying attendance events.

Run the digest sender manually:

```bash
python manage.py send_attendance_daily_digest
```

Run for a specific date:

```bash
python manage.py send_attendance_daily_digest --date 2026-04-13
```

Run for a custom period:

```bash
python manage.py send_attendance_daily_digest --start-date 2026-04-01 --end-date 2026-04-07
```

For production use, schedule this command externally (for example, cron or Windows Task Scheduler).

## Sample Workflows

### Identify Chronic Absences
1. Go to Reports
2. Set date range to last semester/term
3. Review "Students with Most Absences" table
4. Export CSV for detailed records
5. Contact guardians for students with high absences

### Weekly Attendance Review
1. Set date range to last 7 days
2. Review daily trends chart
3. Check for any unusual patterns (spike in absences)
4. Export PDF for weekly staff meeting

### Individual Student Report
1. Select specific student from filter
2. Set desired date range
3. Review all records in table
4. Export CSV for parent-teacher conference

### Classroom Performance
1. Select specific classroom
2. Review status distribution chart
3. Check percentage of present vs. absent
4. Export PDF for principal review

## Tips for Best Results

- **Wider Date Ranges**: Use longer periods (30+ days) for meaningful trend analysis
- **Combine Filters**: Stack multiple filters (classroom + date range) for focused insights
- **Regular Reviews**: Check reports weekly to catch patterns early
- **Export Regularly**: Keep CSV archives for historical comparison
- **Share With Guardians**: Use PDF exports in parent communications

## Troubleshooting

### No Data Showing
- **Cause**: No attendance records match your filters
- **Solution**: Expand date range or remove some filters

### Chart Not Displaying
- **Cause**: JavaScript not loading or browser compatibility
- **Solution**: Refresh page, ensure JavaScript is enabled, try another browser

### PDF Export Error
- **Cause**: `reportlab` library not installed
- **Solution**: Install via `pip install reportlab` and restart server

### Slow Loading
- **Cause**: Very large date ranges with many records
- **Solution**: Narrow date range or add more specific filters

## Questions?

Contact your system administrator for:
- Access permission issues
- Data discrepancies
- Feature requests
- Technical problems

---

**Last Updated**: February 2026  
**Feature Version**: 1.0
