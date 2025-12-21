// src/components/ContactCard.tsx
import React from 'react';
import { Contact } from '../../models/Contact';

interface ContactCardProps {
  contact: Contact;
  onEdit?: () => void;
  onDelete?: () => void;
}

const ContactCard: React.FC<ContactCardProps> = ({ contact, onEdit, onDelete }) => {
  return (
    <div className="contact-card">
      <div className="contact-avatar">
        {contact.avatar ? (
          <img src={contact.avatar} alt={contact.name} />
        ) : (
          <div className="avatar-placeholder">
            {contact.name.charAt(0).toUpperCase()}
          </div>
        )}
      </div>
      <div className="contact-info">
        <h3 className="contact-name">{contact.name}</h3>
        <p className="contact-email">{contact.email}</p>
        <p className="contact-phone">{contact.phone}</p>
        <p className="contact-company">{contact.company}</p>
        <div className="contact-meta">
          <span className="contact-created">
            Created: {new Date(contact.createdAt).toLocaleDateString()}
          </span>
          <span className="contact-updated">
            Updated: {new Date(contact.updatedAt).toLocaleDateString()}
          </span>
        </div>
      </div>
      <div className="contact-actions">
        {onEdit && (
          <button className="edit-btn" onClick={onEdit}>
            Edit
          </button>
        )}
        {onDelete && (
          <button className="delete-btn" onClick={onDelete}>
            Delete
          </button>
        )}
      </div>
    </div>
  );
};

export default ContactCard;

// src/components/ContactList.tsx
import React, { useState, useEffect } from 'react';
import { Contact } from '../../models/Contact';
import ContactCard from './ContactCard';

interface ContactListProps {
  contacts: Contact[];
  onEdit?: (contact: Contact) => void;
  onDelete?: (contact: Contact) => void;
  onSearch?: (query: string) => void;
}

const ContactList: React.FC<ContactListProps> = ({ contacts, onEdit, onDelete, onSearch }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredContacts, setFilteredContacts] = useState<Contact[]>(contacts);

  useEffect(() => {
    if (onSearch) {
      onSearch(searchQuery);
    }
  }, [searchQuery, onSearch]);

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredContacts(contacts);
    } else {
      const filtered = contacts.filter(contact =>
        contact.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        contact.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
        contact.phone.toLowerCase().includes(searchQuery.toLowerCase()) ||
        contact.company.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredContacts(filtered);
    }
  }, [contacts, searchQuery]);

  return (
    <div className="contact-list">
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search contacts..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>
      <div className="contact-grid">
        {filteredContacts.map((contact) => (
          <ContactCard
            key={contact.id}
            contact={contact}
            onEdit={onEdit}
            onDelete={onDelete}
          />
        ))}
      </div>
    </div>
  );
};

export default ContactList;

// src/models/Contact.ts
export interface Contact {
  id: string;
  name: string;
  email: string;
  phone: string;
  company: string;
  createdAt: string;
  updatedAt: string;
  avatar?: string;
  notes?: Note[];
  deals?: Deal[];
}

export interface Note {
  id: string;
  content: string;
  createdAt: string;
  updatedAt: string;
  author: string;
}

export interface Deal {
  id: string;
  name: string;
  amount: number;
  stage: 'Prospecting' | 'Negotiation' | 'Closed Won' | 'Closed Lost';
  closeDate: string;
  contactId: string;
  createdAt: string;
  updatedAt: string;
  notes?: Note[];
}

// src/styles/ContactCard.module.css
.contact-card {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.contact-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #2a2a2a;
}

.contact-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.avatar-placeholder {
  color: #fff;
  font-weight: bold;
  background: #4a4a4a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.contact-info {
  flex: 1;
}

.contact-name {
  font-size: 1.5rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.contact-email {
  color: #aaa;
  font-size: 1rem;
  margin: 0.25rem 0;
}

.contact-phone {
  color: #aaa;
  font-size: 1rem;
  margin: 0.25rem 0;
}

.contact-company {
  color: #aaa;
  font-size: 1rem;
  margin: 0.25rem 0;
}

.contact-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #aaa;
}

.contact-created, .contact-updated {
  padding: 0.25rem 0.5rem;
  background: #333;
  border-radius: 4px;
}

.contact-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.edit-btn, .delete-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
}

.edit-btn {
  background: #4caf50;
  color: #fff;
}

.edit-btn:hover {
  background: #45a049;
}

.delete-btn {
  background: #f44336;
  color: #fff;
}

.delete-btn:hover {
  background: #d32f2f;
}

// src/styles/ContactList.module.css
.contact-list {
  padding: 1rem;
}

.search-bar {
  margin-bottom: 1rem;
}

.search-bar input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #4a4a4a;
  border-radius: 6px;
  background: #2a2a2a;
  color: #fff;
  font-size: 1rem;
  outline: none;
}

.contact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

// src/App.tsx
import React, { useState, useEffect } from 'react';
import ContactList from './components/ContactList';
import { Contact } from './models/Contact';

const App: React.FC = () => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    // Mock data for demonstration
    const mockContacts: Contact[] = [
      {
        id: '1',
        name: 'John Doe',
        email: 'john.doe@example.com',
        phone: '+1 (555) 123-4567',
        company: 'TechCorp',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        avatar: 'https://via.placeholder.com/150',
      },
      {
        id: '2',
        name: 'Jane Smith',
        email: 'jane.smith@example.com',
        phone: '+1 (555) 987-6543',
        company: 'Startup Inc.',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        avatar: 'https://via.placeholder.com/150',
      },
      {
        id: '3',
        name: 'Mike Johnson',
        email: 'mike.johnson@example.com',
        phone: '+1 (555) 444-3333',
        company: 'Global Solutions',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        avatar: 'https://via.placeholder.com/150',
      },
    ];

    setContacts(mockContacts);
  }, []);

  const handleEdit = (contact: Contact) => {
    console.log('Edit contact:', contact);
  };

  const handleDelete = (contact: Contact) => {
    console.log('Delete contact:', contact);
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>CRM Dashboard</h1>
      </header>
      <main className="app-main">
        <ContactList
          contacts={contacts}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onSearch={handleSearch}
        />
      </main>
    </div>
  );
};

export default App;

// src/styles/App.module.css
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #121212;
  color: #fff;
}

.app-header {
  background: #2a2a2a;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #333;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.app-header h1 {
  font-size: 1.875rem;
  font-weight: 700;
  color: #fff;
}

.app-main {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

// src/models/Deal.ts
export interface Deal {
  id: string;
  name: string;
  value: number;
  stage: string;
  contact_id: string;
  pipeline_id: string;
  created_at: string;
  updated_at: string;
}

export const defaultDeal: Deal = {
  id: '',
  name: '',
  value: 0,
  stage: '',
  contact_id: '',
  pipeline_id: '',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

// src/components/DealCard.tsx
import React from 'react';
import { Deal } from '../../models/Deal';

interface DealCardProps {
  deal: Deal;
  onEdit?: (deal: Deal) => void;
  onDelete?: (deal: Deal) => void;
}

const DealCard: React.FC<DealCardProps> = ({ deal, onEdit, onDelete }) => {
  return (
    <div className="deal-card">
      <div className="deal-header">
        <h3 className="deal-name">{deal.name}</h3>
        <span className="deal-stage">{deal.stage}</span>
      </div>
      <div className="deal-details">
        <p className="deal-value">Value: ${deal.value.toLocaleString()}</p>
        <p className="deal-created">
          Created: {new Date(deal.created_at).toLocaleDateString()}
        </p>
        <p className="deal-updated">
          Updated: {new Date(deal.updated_at).toLocaleDateString()}
        </p>
      </div>
      <div className="deal-actions">
        {onEdit && (
          <button className="edit-btn" onClick={() => onEdit(deal)}>
            Edit
          </button>
        )}
        {onDelete && (
          <button className="delete-btn" onClick={() => onDelete(deal)}>
            Delete
          </button>
        )}
      </div>
    </div>
  );
};

export default DealCard;

// src/components/DealList.tsx
import React, { useState, useEffect } from 'react';
import { Deal } from '../../models/Deal';
import DealCard from './DealCard';

interface DealListProps {
  deals: Deal[];
  onEdit?: (deal: Deal) => void;
  onDelete?: (deal: Deal) => void;
  onSearch?: (query: string) => void;
}

const DealList: React.FC<DealListProps> = ({ deals, onEdit, onDelete, onSearch }) => {
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (onSearch) {
      onSearch(searchQuery);
    }
  }, [searchQuery, onSearch]);

  const filteredDeals = deals.filter(deal =>
    deal.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="deal-list-container">
      <div className="deal-list-header">
        <h2>Deals</h2>
        <input
          type="text"
          placeholder="Search deals..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
      </div>
      <div className="deal-list">
        {filteredDeals.length > 0 ? (
          filteredDeals.map(deal => (
            <DealCard
              key={deal.id}
              deal={deal}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          ))
        ) : (
          <p className="no-deals">No deals found.</p>
        )}
      </div>
    </div>
  );
};

export default DealList;

// src/styles/deals.module.css
.deal-list-container {
  background-color: #1a1a1a;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.deal-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.deal-list-header h2 {
  color: #ffffff;
  font-size: 24px;
  font-weight: 600;
}

.search-input {
  background-color: #2d2d2d;
  border: 1px solid #444;
  border-radius: 6px;
  color: #ffffff;
  padding: 8px 16px;
  width: 250px;
  font-size: 14px;
}

.deal-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.deal-card {
  background-color: #2d2d2d;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s ease-in-out;
}

.deal-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.deal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.deal-name {
  color: #ffffff;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.deal-stage {
  color: #66ccff;
  font-size: 14px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 4px;
  background-color: #1a1a1a;
}

.deal-details {
  margin: 16px 0;
}

.deal-value {
  color: #ffffff;
  font-size: 16px;
  font-weight: 500;
}

.deal-created,
.deal-updated {
  color: #aaa;
  font-size: 12px;
  margin: 4px 0;
}

.deal-actions {
  display: flex;
  gap: 10px;
}

.edit-btn,
.delete-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.edit-btn {
  background-color: #4CAF50;
  color: white;
}

.edit-btn:hover {
  background-color: #45a049;
}

.delete-btn {
  background-color: #f44336;
  color: white;
}

.delete-btn:hover {
  background-color: #d32f2f;
}

.no-deals {
  color: #aaa;
  text-align: center;
  padding: 20px;
  font-size: 16px;
}

// src/components/PipelineList.tsx
import React from 'react';
import { Pipeline } from '../../models/Pipeline';

interface PipelineListProps {
  pipelines: Pipeline[];
  onEdit?: (pipeline: Pipeline) => void;
  onDelete?: (pipeline: Pipeline) => void;
}

const PipelineList: React.FC<PipelineListProps> = ({ pipelines, onEdit, onDelete }) => {
  return (
    <div className="pipeline-list">
      {pipelines.map((pipeline) => (
        <div key={pipeline.id} className="pipeline-item">
          <h4 className="pipeline-name">{pipeline.name}</h4>
          <p className="pipeline-stage-order">Stage Order: {pipeline.stage_order}</p>
          <p className="pipeline-created">
            Created: {new Date(pipeline.created_at).toLocaleDateString()}
          </p>
          {onEdit && (
            <button className="edit-btn" onClick={() => onEdit(pipeline)}>
              Edit
            </button>
          )}
          {onDelete && (
            <button className="delete-btn" onClick={() => onDelete(pipeline)}>
              Delete
            </button>
          )}
        </div>
      ))}
    </div>
  );
};

export default PipelineList;

// src/components/PipelineCard.tsx
import React from 'react';
import { Pipeline } from '../../models/Pipeline';

interface PipelineCardProps {
  pipeline: Pipeline;
  onEdit?: (pipeline: Pipeline) => void;
  onDelete?: (pipeline: Pipeline) => void;
}

const PipelineCard: React.FC<PipelineCardProps> = ({ pipeline, onEdit, onDelete }) => {
  return (
    <div className="pipeline-card">
      <div className="pipeline-header">
        <h3 className="pipeline-name">{pipeline.name}</h3>
        <span className="pipeline-stage-order">Stage Order: {pipeline.stage_order}</span>
      </div>
      <div className="pipeline-details">
        <p className="pipeline-created">
          Created: {new Date(pipeline.created_at).toLocaleDateString()}
        </p>
      </div>
      <div className="pipeline-actions">
        {onEdit && (
          <button className="edit-btn" onClick={() => onEdit(pipeline)}>
            Edit
          </button>
        )}
        {onDelete && (
          <button className="delete-btn" onClick={() => onDelete(pipeline)}>
            Delete
          </button>
        )}
      </div>
    </div>
  );
};

export default PipelineCard;

// src/App.tsx
import React, { useState } from 'react';
import PipelineList from './components/PipelineList';
import DealList from './components/DealList';
import ContactList from './components/ContactList';
import NoteList from './components/NoteList';
import SearchBar from './components/SearchBar';

function App() {
  const [pipelines, setPipelines] = useState([
    {
      id: '1',
      name: 'Sales Pipeline',
      stage_order: 1,
      created_at: '2025-01-01T00:00:00Z',
    },
    {
      id: '2',
      name: 'Marketing Pipeline',
      stage_order: 2,
      created_at: '2025-01-02T00:00:00Z',
    },
  ]);

  const [deals, setDeals] = useState([
    {
      id: '1',
      name: 'Deal 1',
      stage: 'Prospecting',
      value: 10000,
      created_at: '2025-01-03T00:00:00Z',
      updated_at: '2025-01-03T00:00:00Z',
    },
  ]);

  const [contacts, setContacts] = useState([
    {
      id: '1',
      name: 'John Doe',
      email: 'john.doe@example.com',
      phone: '123-456-7890',
      created_at: '2025-01-04T00:00:00Z',
    },
  ]);

  const [notes, setNotes] = useState([
    {
      id: '1',
      title: 'Note 1',
      content: 'This is a note.',
      created_at: '2025-01-05T00:00:00Z',
    },
  ]);

  const handlePipelineEdit = (pipeline: any) => {
    console.log('Editing pipeline:', pipeline);
  };

  const handlePipelineDelete = (pipeline: any) => {
    console.log('Deleting pipeline:', pipeline);
  };

  const handleDealEdit = (deal: any) => {
    console.log('Editing deal:', deal);
  };

  const handleDealDelete = (deal: any) => {
    console.log('Deleting deal:', deal);
  };

  const handleContactEdit = (contact: any) => {
    console.log('Editing contact:', contact);
  };

  const handleContactDelete = (contact: any) => {
    console.log('Deleting contact:', contact);
  };

  const handleNoteEdit = (note: any) => {
    console.log('Editing note:', note);
  };

  const handleNoteDelete = (note: any) => {
    console.log('Deleting note:', note);
  };

  return (
    <div className="app">
      <h1>CRM Dashboard</h1>
      <div className="dashboard">
        <div className="sidebar">
          <h2>Navigation</h2>
          <ul>
            <li>Pipelines</li>
            <li>Deals</li>
            <li>Contacts</li>
            <li>Notes</li>
            <li>Search</li>
          </ul>
        </div>
        <div className="content">
          <h2>Pipelines</h2>
          <PipelineList
            pipelines={pipelines}
            onEdit={handlePipelineEdit}
            onDelete={handlePipelineDelete}
          />
          <h2>Deals</h2>
          <DealList
            deals={deals}
            onEdit={handleDealEdit}
            onDelete={handleDealDelete}
          />
          <h2>Contacts</h2>
          <ContactList
            contacts={contacts}
            onEdit={handleContactEdit}
            onDelete={handleContactDelete}
          />
          <h2>Notes</h2>
          <NoteList
            notes={notes}
            onEdit={handleNoteEdit}
            onDelete={handleNoteDelete}
          />
          <h2>Search</h2>
          <SearchBar />
        </div>
      </div>
    </div>
  );
}

export default App;

// src/index.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

interface PipelineCardProps {
  id: string;
  content: string;
  contact_id?: string; // default: system-generated
  deal_id?: string;   // default: system-generated
  created_at: string; // ISO format
  author: string;
}

// PipelineCard.tsx (completed version)
import React from 'react';
import { Button } from '@/components/ui/button'; // Assuming Tailwind UI components

interface PipelineCardProps {
  id: string;
  content: string;
  contact_id?: string;
  deal_id?: string;
  created_at: string;
  author: string;
}

export const PipelineCard: React.FC<PipelineCardProps> = ({
  id,
  content,
  contact_id = 'sys-gen-' + id,
  deal_id = 'sys-gen-' + id,
  created_at,
  author,
}) => {
  const stageOrder = "Stage 1 of 5"; // Placeholder — to be dynamically calculated later

  return (
    <div className="border rounded-lg p-4 shadow-sm bg-white">
      <h3 className="font-semibold text-lg">{content}</h3>
      <p className="text-sm text-gray-600 mt-1">
        {stageOrder} • {new Date(created_at).toLocaleDateString()}
      </p>
      <div className="flex justify-between mt-4">
        <span className="text-xs text-gray-500">By {author}</span>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">Edit</Button>
          <Button variant="outline" size="sm">Delete</Button>
        </div>
      </div>
    </div>
  );
};

import React from 'react';
import { Button } from '@/components/ui/button';

interface PipelineCardProps {
  id: string;
  content: string;
  contact_id?: string;
  deal_id?: string;
  created_at: string;
  author: string;
}

export const PipelineCard: React.FC<PipelineCardProps> = ({
  id,
  content,
  contact_id = 'sys-gen-' + id,
  deal_id = 'sy

import React from 'react';
import { Button } from '@/components/ui/button';

interface PipelineCardProps {
  id: string;
  name: string; // Updated from 'content' to match context
  stage: string;
  stage_order: number;
  created_at: string;
  author: string;
  contact_id?: string;
  deal_id?: string;
  onEdit?: () => void;
  onDelete?: () => void;
}

export const PipelineCard: React.FC<PipelineCardProps> = ({
  id,
  name,
  stage,
  stage_order,
  created_at,
  author,
  contact_id = 'sys-gen-' + id,
  deal_id = 'sys-deal-' + id,
  onEdit,
  onDelete,
}) => {
  return (
    <div className="border rounded-lg p-4 bg-white shadow-sm hover:shadow-md transition-shadow duration-200 flex flex-col">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h3 className="font-semibold text-lg text-gray-900 mb-1">{name}</h3>
          <p className="text-sm text-gray-600 mb-2">
            Stage: {stage} • Order: {stage_order}
          </p>
          <p className="text-sm text-gray-500">
            Created: {new Date(created_at).toLocaleDateString()} • By: {author}
          </p>
        </div>
        <div className="flex space-x-2">
          {onEdit && (
            <Button
              onClick={onEdit}
              variant="outline"
              className="btn-outline-secondary text-sm px-3 py-1.5"
              size="sm"
            >
              Edit
            </Button>
          )}
          {onDelete && (
            <Button
              onClick={onDelete}
              variant="outline"
              className="btn-outline-secondary text-sm px-3 py-1.5"
              size="sm"
            >
              Delete
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

// Optional: Add responsive styling if needed (e.g., for mobile)
// You can extend this component with media queries or flex utilities as needed.

// Add a "View Details" button for richer interaction
{onView && (
  <Button
    onClick={onView}
    variant="outline"
    className="btn-outline-secondary text-sm px-3 py-1.5"
    size="sm"
  >
    View Details
  </Button>
)}

import React, { useState, useEffect } from 'react';

const NotesList = () => {
  const [notes, setNotes] = useState([]);

  useEffect(() => {
    // Simulate API call
    const mockNotes = [
      { id: 1, title: "Meeting Notes", content: "Discussed Q4 goals and resource allocation.", createdAt: "2025-12-15T10:30:00Z" },
      { id: 2, title: "Project Update", content: "Backend API is ready for integration.", createdAt: "2025-12-14T14:20:00Z" },
    ];
    setNotes(mockNotes);
  }, []);

  return (
    <div className="notes-list">
      {notes.map(note => (
        <div key={note.id} className="note-card">
          <h3>{note.title}</h3>
          <p>{note.content}</p>
          <small>{new Date(note.createdAt).toLocaleString()}</small>
          <button onClick={() => alert(`Viewing note: ${note.title}`)}>View Details</button>
        </div>
      ))}
    </div>
  );
};

export default NotesList;

import React, { useState, useEffect } from 'react';

const NotesList = () => {
  const [notes, setNotes] = useState([]);
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<{ tag?: string; dateRange?: string }>({});
  const [loading, setLoading] = useState(false);

  // Simulate API call with search and filters
  const fetchNotes = async () => {
    setLoading(true);
    try {
      const result = await searchNotes(query, filters);
      setNotes(result);
    } catch (error) {
      console.error('Error fetching notes:', error);
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchNotes();
  }, []);

  // Re-fetch when query or filters change
  useEffect(() => {
    fetchNotes();
  }, [query, filters]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchNotes();
  };

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="notes-list">
      <form onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Search notes..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit">Search</button>
      </form>

      <div className="filters">
        <label>
          Tag:
          <input
            type="text"
            name="tag"
            value={filters.tag || ''}
            onChange={handleFilterChange}
          />
        </label>
        <label>
          Date Range:
          <input
            type="text"
            name="dateRange"
            value={filters.dateRange || ''}
            onChange={handleFilterChange}
            placeholder="YYYY-MM-DD to YYYY-MM-DD"
          />
        </label>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="notes-grid">
          {notes.length === 0 ? (
            <p>No notes found.</p>
          ) : (
            notes.map(note => (
              <div key={note.id} className="note-card">
                <h3>{note.title}</h3>
                <p>{note.content}</p>
                <small>{new Date(note.createdAt).toLocaleString()}</small>
                <div className="tags">
                  {note.tags.map(tag => (
                    <span key={tag} className="tag">{tag}</span>
                  ))}
                </div>
                <button className="btn">View Details</button>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default NotesList;