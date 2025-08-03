# Railway Deployment Debug Guide

## Current Status
Your Railway app is now enhanced with comprehensive debugging and database auto-initialization.

## What's Fixed
1. **Database Schema Issues**: Added PostgreSQL-compatible table creation
2. **Database Auto-Initialization**: Tables are created automatically on startup
3. **Enhanced Debugging**: Comprehensive logging for all board operations
4. **File Upload Debugging**: Detailed error tracking for photo uploads

## Debug Output You'll See
When you test your Railway app, you'll now see detailed logs like:

### App Startup:
```
✅ Upload directory created/verified: /tmp/uploads
📁 Directory exists: true
📝 Directory writable: true
✅ PostgreSQL tables initialized successfully
```

### Adding a Board:
```
🆕 Adding new board...
📋 Form data received: {'date': '2024-01-01', 'roman_number': 'I', ...}
📝 Processed form data: date=2024-01-01, roman_number=I, is_gift=0, in_collection=1
🖼️ Processing front image: my_board.jpg
📁 Upload folder: /tmp/uploads
💾 Saving to: /tmp/uploads/front_1672531200_abc12345_my_board.jpg
✅ Front image saved successfully
💾 Inserting board into database...
✅ Board inserted successfully with ID: 1
```

### Editing a Board:
```
✏️ Editing board ID: 1
📋 Form data received: {'date': '2024-01-02', ...}
```

### Deleting a Board:
```
🗑️ Deleting board ID: 1
✅ Board found, proceeding with deletion
✅ Board deleted successfully from database
```

## Testing Your Railway App
1. **Add a Board**: Test the form submission and photo uploads
2. **Edit a Board**: Click edit button from board detail page
3. **Delete a Board**: Use the delete button (with confirmation)

## If Issues Persist
The debug output will now show exactly where problems occur:
- Database connection issues
- Form processing problems
- File upload failures
- Query execution errors

Check your Railway logs for these debug messages to identify the specific issue.

## Database Schema
The app now automatically creates these PostgreSQL tables:
- `boards` (with SERIAL PRIMARY KEY)
- `players` (with SERIAL PRIMARY KEY) 
- `games` (with SERIAL PRIMARY KEY)
- `wood_types` (with SERIAL PRIMARY KEY)
- `material_types` (with SERIAL PRIMARY KEY)

## Next Steps
1. Deploy the updated code to Railway
2. Test each board operation (add/edit/delete)
3. Check Railway logs for debug output
4. Report any specific error messages you see
