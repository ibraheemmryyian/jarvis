const renderEmailTemplate = (template: EmailTemplate, audience: "C-suite" | "SME") => {
  if (audience === "C-suite") {
    return template.body.replace("[Your Name]", "Alex Chen");
  } else {
    return template.body.replace("[First Name]", "Jane Doe");
  }
};

// Example: Main App Layout
function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Navbar />
      <main className="container mx-auto px-6 py-12">
        <UploadSection />
        <EmailPreviewSection />
        <GenerateButton />
      </main>
      <Footer />
    </div>
  );
}

function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Navbar />
      <main className="container mx-auto px-6 py-12">
        <UploadSection />
        <EmailPreviewSection />
        <GenerateButton />
      </main>
      <Footer />
    </div>
  );
}