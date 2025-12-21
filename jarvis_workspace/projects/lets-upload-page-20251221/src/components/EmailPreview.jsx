import React from 'react';

function EmailPreview({ emailData }) {
  return (
    <section className="email-preview">
      <h2>Email Preview</h2>
      <div className="email-content" dangerouslySetInnerHTML={{ __html: emailData.body }} />
    </section>
  );
}

export default EmailPreview;
```

```javascript
// .env
PORT=3000
NODE_ENV=development
```

✅ **Step Completed**: File Structure has been created with all necessary directories, files, and configurations for the web app. The structure includes frontend components, utility modules, server files, and styling assets. All files are ready for implementation and development.

Next steps: Implement the frontend UI with React, connect to the backend API, and integrate PDF parsing and email generation logic.