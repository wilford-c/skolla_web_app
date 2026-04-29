# HTMX Quick Reference Card

## Essential HTMX Attributes

```html
<!-- GET request on click -->
<button hx-get="/url">Click Me</button>

<!-- POST form with HTMX -->
<form hx-post="/submit" hx-target="#result">
    <input name="data" />
    <button type="submit">Submit</button>
</form>

<!-- Live search (debounced) -->
<input 
    hx-get="/search" 
    hx-trigger="input changed delay:300ms"
    hx-target="#results" />

<!-- Delete with confirmation -->
<button 
    hx-delete="/item/1"
    hx-confirm="Delete this item?"
    hx-target="closest tr"
    hx-swap="outerHTML">Delete</button>

<!-- Auto-refresh every 30 seconds -->
<div hx-get="/status" hx-trigger="every 30s"></div>

<!-- Load on scroll (infinite scroll) -->
<div hx-get="/next-page" hx-trigger="revealed"></div>

<!-- Inline edit pattern -->
<div hx-get="/edit/1" hx-swap="outerHTML">
    View Mode - Click to Edit
</div>
```

## Common Triggers

- `click` - On click (default for buttons)
- `change` - On value change (default for inputs)
- `submit` - On form submit
- `input` - On every keystroke
- `load` - On element load
- `revealed` - When element scrolls into view
- `every 30s` - Poll every 30 seconds
- `input changed delay:300ms` - Debounced input
- `mouseenter, mouseleave` - Hover events

## Swap Strategies

- `innerHTML` - Replace inner HTML (default)
- `outerHTML` - Replace entire element
- `beforebegin` - Insert before element
- `afterbegin` - Insert at start of element
- `beforeend` - Insert at end of element
- `afterend` - Insert after element
- `delete` - Delete target element
- `none` - Don't swap, just trigger events

## Target Selectors

- `#id` - By ID
- `.class` - By class
- `closest tr` - Nearest parent TR
- `next div` - Next sibling DIV
- `previous` - Previous element
- `find .class` - Find child by class

## Django View Pattern

```python
@login_required
def my_htmx_view(request):
    # Process data
    items = Item.objects.filter(...)
    
    # Return partial for HTMX, full page otherwise
    if request.headers.get('HX-Request'):
        return render(request, 'app/partials/items.html', {
            'items': items
        })
    
    return render(request, 'app/full_page.html', {
        'items': items
    })
```

## CSRF Token (Already Configured)

CSRF is automatically handled in `base.html`. No action needed.

## Class Reference

```css
/* Hide by default, show during request */
.htmx-indicator { display: none; }
.htmx-request .htmx-indicator { display: inline; }
.htmx-request.htmx-indicator { display: inline; }
```

## File Organization

```
templates/
  app_name/
    list.html          # Full page
    form.html          # Full page
    partials/
      items.html       # HTMX partial
      form.html        # HTMX partial
      row.html         # HTMX partial
```
