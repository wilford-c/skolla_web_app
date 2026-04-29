# Sprint User Stories - Skola School Management Platform

## 1. User Profile Management

### US-001: View User Profile
**As a** logged-in user  
**I want to** view my profile information  
**So that** I can see my personal details, role, and account information

**Acceptance Criteria:**
- Users can navigate to "My Profile" from the sidebar
- Profile displays name, email, role, username, and date joined
- Profile view is read-only with an "Edit Profile" button

### US-002: Edit User Profile
**As a** logged-in user  
**I want to** edit my profile information  
**So that** I can keep my personal details up to date

**Acceptance Criteria:**
- Users can click "Edit Profile" to access edit form
- Users can update first name, last name, and email
- Form validates required fields
- Success message displays after saving
- Users are redirected back to profile view

### US-003: Change Password
**As a** logged-in user  
**I want to** change my password  
**So that** I can maintain account security

**Acceptance Criteria:**
- Users can access password change from profile page
- Form requires old password, new password, and confirmation
- Password validation enforces security requirements
- Success message displays after password change
- User remains logged in after password change

---

## 2. Announcements System

### US-004: View Announcements
**As a** user  
**I want to** view school announcements  
**So that** I can stay informed about important updates and events

**Acceptance Criteria:**
- All users can view published announcements
- Announcements display with title, content, author, date, and category
- List view shows announcement cards with summary
- Detail view shows full announcement with attachments
- Announcements are ordered by publication date (newest first)

### US-005: Create Announcements
**As an** admin or staff member  
**I want to** create announcements  
**So that** I can communicate important information to the school community

**Acceptance Criteria:**
- Only admins and staff can access announcement creation
- Form includes title, content, category, target audience, and priority
- Can upload multiple file attachments (images, PDFs, documents)
- Can set announcement as published or draft
- Success message displays after creation
- Redirects to announcement detail page

### US-006: Edit Announcements
**As an** admin or staff member  
**I want to** edit existing announcements  
**So that** I can correct errors or update information

**Acceptance Criteria:**
- Only admins and staff can edit announcements
- Edit form pre-populates with existing data
- Can add, remove, or replace attachments
- Can change publication status
- Edit/Delete buttons visible only to authorized users
- Success message displays after update

### US-007: Delete Announcements
**As an** admin or staff member  
**I want to** delete announcements  
**So that** I can remove outdated or incorrect information

**Acceptance Criteria:**
- Only admins and staff can delete announcements
- Confirmation page displays before deletion
- Shows warning about permanent deletion
- Delete is irreversible
- Redirects to announcements list after deletion

---

## 3. Calendar Events

### US-008: View School Calendar
**As a** user  
**I want to** view school events on a calendar  
**So that** I can plan and stay aware of upcoming activities

**Acceptance Criteria:**
- Calendar displays events by date
- Events show title, description, location, and times
- Different event types have color coding
- Users can see event details by clicking on events
- Calendar shows current month by default

---

## 4. Assignments System

### US-009: View Assignments (Student)
**As a** student  
**I want to** view my assignments  
**So that** I can see what work I need to complete

**Acceptance Criteria:**
- Students see assignments for their enrolled classes
- List shows assignment title, subject, due date, and status
- Overdue assignments are clearly marked
- Can view full assignment details
- Can see submission status (submitted/not submitted)

### US-010: Submit Assignment
**As a** student  
**I want to** submit my completed assignment  
**So that** my teacher can grade my work

**Acceptance Criteria:**
- Students can access submission form from assignment detail
- Can upload multiple files (documents, images)
- Can add submission comments
- Shows confirmation before final submission
- Cannot submit after deadline (unless late submissions allowed)
- Receives confirmation after successful submission

### US-011: Create Assignment (Teacher)
**As a** teacher  
**I want to** create assignments  
**So that** I can assign work to my students

**Acceptance Criteria:**
- Teachers can create assignments for their classes
- Form includes title, description, instructions, subject, classroom
- Can set assigned date, due date, and maximum marks
- Can set status (draft/published)
- Can toggle late submission permission
- Can attach reference materials
- Success message and redirect to assignment detail

### US-012: Edit Assignment (Teacher)
**As a** teacher  
**I want to** edit my assignments  
**So that** I can update requirements or correct mistakes

**Acceptance Criteria:**
- Teachers can only edit their own assignments (admins can edit all)
- Edit form pre-populates with existing data
- Can manage attachments (add/remove)
- Can change all assignment details
- Student submissions are not affected by edits
- Success message displays after update

### US-013: Delete Assignment (Teacher)
**As a** teacher  
**I want to** delete assignments  
**So that** I can remove cancelled or duplicate assignments

**Acceptance Criteria:**
- Teachers can only delete their own assignments (admins can delete all)
- Confirmation page shows assignment details
- Warning if assignment has student submissions
- Deletion removes assignment and all submissions
- Confirmation required before deletion
- Redirects to assignments list

---

## 5. Messaging System

### US-014: View Message Inbox
**As a** user  
**I want to** view my message conversations  
**So that** I can read and manage my communications

**Acceptance Criteria:**
- Inbox shows all conversations involving the user
- Displays conversation subject, participants, last message, and time
- Shows unread message count badge
- Conversations ordered by most recent activity
- Can click conversation to view full thread

### US-015: Start New Conversation
**As a** user  
**I want to** send a message to other users  
**So that** I can communicate with teachers, staff, or students

**Acceptance Criteria:**
- Can select multiple recipients from available users list
- Recipients filtered by role-based permissions
- Must enter subject and message content
- Can attach files to initial message
- Creates conversation and sends to all participants
- Redirects to conversation view

### US-016: Send Message in Conversation
**As a** user  
**I want to** reply to conversations  
**So that** I can continue communication threads

**Acceptance Criteria:**
- Can send messages within existing conversations
- Can attach files to replies
- Message displays immediately after sending
- All participants can see the message
- Timestamp shows when message was sent
- Sender name displayed with each message

### US-017: View Message Status
**As a** message sender  
**I want to** see if my messages have been read  
**So that** I know when recipients have seen my communication

**Acceptance Criteria:**
- Read receipts track when messages are opened
- Can see which participants have read messages
- Read status updates automatically
- Unread conversations highlighted in inbox

---

## 6. Notification System

### US-018: Receive In-App Notifications
**As a** user  
**I want to** receive notifications about important events  
**So that** I don't miss messages, assignments, or announcements

**Acceptance Criteria:**
- Notification bell icon in header shows unread count
- Badge displays number of unread notifications
- Bell animates when new notification arrives
- Clicking bell navigates to notifications page
- Notifications auto-update every 30 seconds

### US-019: View All Notifications
**As a** user  
**I want to** see all my notifications in one place  
**So that** I can review and act on them

**Acceptance Criteria:**
- Notifications page lists all notifications
- Each notification shows type, title, message, and time
- Different notification types have colored icons
- Unread notifications are highlighted
- Can mark individual notifications as read
- Can mark all notifications as read at once
- Action buttons link to relevant content

### US-020: Receive Notifications for Messages
**As a** user  
**I want to** be notified when I receive new messages  
**So that** I can respond promptly

**Acceptance Criteria:**
- Notification created when user receives a message
- Shows sender name and message preview
- Links directly to conversation
- Notification marked as read when conversation is opened

### US-021: Receive Notifications for Assignments
**As a** student  
**I want to** be notified about new assignments  
**So that** I can start working on them

**Acceptance Criteria:**
- Notification created when teacher publishes new assignment
- Shows assignment title, subject, and due date
- Links directly to assignment details
- Only students in the assigned classroom receive notification

### US-022: Receive Notifications for Announcements
**As a** user in target audience  
**I want to** be notified about new announcements  
**So that** I stay informed about school updates

**Acceptance Criteria:**
- Notification created when announcement is published
- Based on target audience setting (All, Students, Teachers, etc.)
- Shows announcement title and preview
- Links to full announcement
- Author does not receive their own announcement notification

---

## 7. Online Status & Last Seen

### US-023: View User Online Status
**As a** user  
**I want to** see if other users are currently online  
**So that** I know if they might respond quickly to messages

**Acceptance Criteria:**
- User status shows as "online", "away", or "offline"
- Online = active within last 60 seconds
- Away = active within last 5 minutes
- Offline = no activity for 5+ minutes
- Status displayed in conversation views
- Status updates based on page activity

### US-024: View Last Seen Time
**As a** user  
**I want to** see when someone was last active  
**So that** I know when they might have seen my message

**Acceptance Criteria:**
- Last seen timestamp displayed for offline users
- Shows relative time (e.g., "5 minutes ago", "2 hours ago")
- Only shows last seen for users you're messaging
- Updates automatically when viewing conversations

---

## 8. File Attachments

### US-025: Upload Files to Messages
**As a** user  
**I want to** attach files to my messages  
**So that** I can share documents, images, and other resources

**Acceptance Criteria:**
- Can attach multiple files when creating conversations
- Can attach files when replying in conversations
- Supports PDFs, Word docs, images, and text files
- Drag-and-drop file upload
- File preview before sending
- Maximum file size validation (10MB per file)

### US-026: Upload Files to Announcements
**As an** admin or staff member  
**I want to** attach files to announcements  
**So that** I can share important documents with the community

**Acceptance Criteria:**
- Can attach multiple files when creating announcements
- Can manage attachments when editing announcements
- Files display with download links in announcement view
- Supports various file types
- Can delete attachments without deleting announcement

### US-027: Upload Files to Assignments
**As a** teacher  
**I want to** attach reference materials to assignments  
**So that** students have the resources they need

**Acceptance Criteria:**
- Can attach multiple files when creating assignments
- Can manage attachments when editing assignments
- Attachments display with download links in assignment view
- Students can download but not delete attachments
- Shows file name and size

---

## Technical Implementation Notes

### Architecture
- Django 5.x backend with SQLite database
- Custom User model with role-based permissions (Admin, Staff, Teacher, Student, Guardian)
- Template-based frontend with inline CSS and vanilla JavaScript
- AJAX polling for real-time notifications (30-second intervals)
- Middleware for automatic user activity tracking

### Security
- Role-based access control using @user_passes_test decorators
- Ownership validation (teachers can only edit/delete their own content)
- CSRF protection on all forms
- File upload validation and sanitization

### Performance
- Query optimization with select_related and prefetch_related
- Database indexing on foreign keys and frequently queried fields
- Efficient caching for user status (5-minute TTL)

### UI/UX
- Responsive design with mobile-first approach
- Modern gradient color scheme
- Card-based layouts
- SVG icons throughout
- Consistent form styling
- Success/error message feedback

---

## Sprint Summary

**Total User Stories:** 27  
**Epic Breakdown:**
- User Management: 3 stories
- Announcements: 4 stories
- Calendar: 1 story
- Assignments: 5 stories
- Messaging: 4 stories
- Notifications: 5 stories
- Online Status: 2 stories
- File Management: 3 stories

**Story Points Completed:** Estimated 89 points (based on complexity)

**Key Achievements:**
✅ Complete CRUD operations for announcements and assignments  
✅ Internal messaging system with multi-participant support  
✅ Real-time notification system with badge updates  
✅ Online status tracking and last seen functionality  
✅ File attachment support across all major features  
✅ Role-based permission system implemented throughout  
✅ Responsive UI with consistent design language  

**Technical Debt:**
- WebSocket implementation for true real-time features (typing indicators, instant online status)
- Email notification delivery system
- Report cards feature (pending)
- Bulk operations for admin tasks
- Advanced search and filtering
- Mobile app considerations
