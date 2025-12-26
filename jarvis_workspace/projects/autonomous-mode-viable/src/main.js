async function fetchContacts() {
    const response = await fetch('/api/contacts', {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer YOUR_ACCESS_TOKEN_HERE'
        }
    });

    if (!response.ok) throw new Error('Network response was not ok.');

    return await response.json();
}

async function displayContacts() {
    try {
        const contacts = await fetchContacts();
        console.log(contacts);
        // Render the contacts on the page
    } catch (error) {
        console.error(error);
    }
}