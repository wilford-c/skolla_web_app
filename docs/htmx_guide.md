# HTMX Integration Guide for Skola

## Overview
HTMX is integrated into Skola to provide real-time UI interactions without writing JavaScript. HTMX allows you to access modern browser features directly from HTML using attributes.

## What's Already Implemented

### 1. **Real-time Notification Badge**
The notification bell automatically updates every 30 seconds without page refresh.

**Location:** Header (all pages)

**Implementation:**
```html
<a href="{% url 'notifications:list' %}" class="notification-bell"
   hx-get="{% url 'notifications:unread_count' %}"
   hx-trigger="load, every 30s"
   hx-target="#notificationBadge"
   hx-swap="outerHTML">
```

**Backend:** `notifications/views.py` - `unread_count()` returns HTML partial

### 2. **Live Student Search**
Real-time search as you type with 300ms debounce.

**Location:** Students List page

**Implementation:**
```html
<input 
    type="search" 
    name="search" 
    placeholder="Search students..."
    hx-get="{% url 'students:search' %}"
    hx-trigger="input changed delay:300ms, search"
    hx-target="#student-table-body"
    hx-indicator="#search-indicator"
/>
```

**Backend:** `students/views.py` - `student_search()` returns filtered table rows

### 3. **In-line Delete with Confirmation**
Delete students with a confirmation dialog and row fade-out animation.

**Location:** Student table rows

**Implementation:**
```html
<form method="post" action="{% url 'students:delete' student.pk %}"
      hx-post="{% url 'students:delete' student.pk %}"
      hx-confirm="Are you sure you want to delete this student?"
      hx-target="closest tr"
      hx-swap="outerHTML swap:1s">
    {% csrf_token %}
    <button class="btn btn-danger btn-small" type="submit">Delete</button>
</form>
```

**Backend:** `students/views.py` - `student_delete()` checks for HX-Request header

## Common HTMX Patterns

### Pattern 1: Load on Scroll (Infinite Scroll)
```html
<div hx-get="/items/next-page/" 
     hx-trigger="revealed" 
     hx-swap="afterend">
    Loading more...
</div>
```

### Pattern 2: Inline Editing
```html
<!-- View Mode -->
<div hx-get="/edit/item/{{ item.id }}/" 
     hx-trigger="click" 
     hx-swap="outerHTML">
    {{ item.name }}
    <button>Edit</button>
</div>

<!-- Edit Mode (returned by server) -->
<form hx-post="/update/item/{{ item.id }}/" 
      hx-swap="outerHTML">
    <input name="name" value="{{ item.name }}" />
    <button type="submit">Save</button>
</form>
```

### Pattern 3: Modal Dialogs
```html
<button hx-get="/modal/confirm-action/" 
        hx-target="#modal-container" 
        hx-swap="innerHTML">
    Open Modal
</button>

<div id="modal-container"></div>
```

### Pattern 4: Form Validation (Live Feedback)
```html
<input name="email" 
       hx-post="/validate/email/" 
       hx-trigger="blur" 
       hx-target="#email-error"
       hx-swap="innerHTML" />
<div id="email-error"></div>
```

### Pattern 5: Dependent Dropdowns
```html
<select name="grade" 
        hx-get="/students/by-grade/" 
        hx-trigger="change" 
        hx-target="#student-select">
    <option value="">Select Grade</option>
    ...
</select>

<select id="student-select" name="student">
    <option>First select a grade</option>
</select>
```

## Creating HTMX Views

### View Template
```python
@login_required
def htmx_view(request):
    # Your query logic
    items = Model.objects.filter(...)
    
    # Check if HTMX request
    if request.headers.get('HX-Request'):
        # Return HTML partial
        return render(request, 'app/partials/items.html', {'items': items})
    
    # Regular request returns full page
    return render(request, 'app/items_page.html', {'items': items})
```

### Partial Template Example
Create partials in `templates/app_name/partials/`:

```html
<!-- students/partials/student_rows.html -->
{% for student in students %}
    <tr>
        <td>{{ student.name }}</td>
        <td>{{ student.email }}</td>
    </tr>
{% empty %}
    <tr><td colspan="2">No students found.</td></tr>
{% endfor %}
```

## HTMX Attributes Reference

### Core Attributes
- `hx-get` - Send GET request to URL
- `hx-post` - Send POST request to URL
- `hx-put` - Send PUT request
- `hx-delete` - Send DELETE request
- `hx-trigger` - Event that triggers request (click, change, input, load, every 30s, etc.)
- `hx-target` - CSS selector for element to update
- `hx-swap` - How to swap the response (innerHTML, outerHTML, beforebegin, afterend, etc.)

### Advanced Attributes
- `hx-confirm` - Show confirmation dialog before request
- `hx-indicator` - Element to show during request
- `hx-push-url` - Update browser URL
- `hx-select` - Select specific part of response
- `hx-vals` - Add additional values to request
- `hx-headers` - Add custom headers
- `hx-include` - Include additional form inputs

### Event Modifiers
- `changed` - Only trigger if value changed
- `delay:300ms` - Debounce delay
- `throttle:1s` - Throttle requests
- `from:body` - Listen for events on body
- `once` - Only trigger once

## CSRF Token Handling

CSRF tokens are automatically added to all HTMX requests via global configuration in `base.html`:

```javascript
document.body.addEventListener('htmx:configRequest', (event) => {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (csrfToken) {
        event.detail.headers['X-CSRFToken'] = csrfToken;
    }
});
```

## Loading Indicators

### Method 1: Using hx-indicator
```html
<div hx-get="/data/" hx-indicator="#spinner">Load</div>
<div id="spinner" class="htmx-indicator">Loading...</div>
```

### Method 2: Global Loading State
Automatically applied to all requests (configured in base.html):

```javascript
document.body.addEventListener('htmx:beforeRequest', (event) => {
    event.detail.target.style.opacity = '0.6';
});

document.body.addEventListener('htmx:afterRequest', (event) => {
    event.detail.target.style.opacity = '1';
});
```

## Best Practices

1. **Use Partials**: Create reusable HTML partials in `templates/app/partials/`
2. **Debounce User Input**: Use `delay:300ms` for search inputs
3. **Provide Feedback**: Use indicators and loading states
4. **Graceful Degradation**: Ensure forms work without JavaScript
5. **Keep Responses Small**: Return only the HTML that needs to update
6. **Use Semantic HTML**: HTMX works best with proper HTML structure
7. **Cache Strategically**: Use `hx-swap="outerHTML"` for content that should update completely

## Testing HTMX Endpoints

### Manual Testing
```bash
# Test if endpoint returns correct HTML
curl -H "HX-Request: true" http://localhost:8000/students/search/?search=john

# Test without HTMX (should return full page for non-HTMX requests)
curl http://localhost:8000/students/search/?search=john
```

### Django Test
```python
def test_htmx_search(self):
    response = self.client.get(
        '/students/search/',
        {'search': 'john'},
        HTTP_HX_REQUEST='true'
    )
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'john')
```

## Next Steps

Consider implementing:
- **Inline editing** for student details
- **Lazy loading** for large tables (load more on scroll)
- **Modal forms** for quick actions
- **Live form validation** with server-side checks
- **Drag and drop** sorting with HTMX
- **Toast notifications** for HTMX responses
- **Progress bars** for long-running operations

## Resources

- [HTMX Documentation](https://htmx.org/docs/)
- [HTMX Examples](https://htmx.org/examples/)
- [HTMX with Django](https://www.photondesigner.com/articles/htmx-django)
