import React from 'react';

function UploadForm({ onFileUpload }) {
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      onFileUpload(file);
    } else {
      alert('Please upload a valid PDF file');
    }
  };

  return (
    <section className="upload-section">
      <h2>Upload Your PDF</h2>
      <p>Drop your 14-page waste valorization report here</p>
      <input
        type="file"
        accept=".pdf"
        onChange={handleFileChange}
        className="upload-input"
        id="pdf-upload"
      />
    </section>
  );
}

export default UploadForm;
```

```javascript