import React, { useState, useEffect } from 'react';
import './ResearchTasksList.css';

const ResearchTasksList = () => {
  const [tasks, setTasks] = useState([]);
  
  useEffect(() => {
    // Fetch tasks from server on component mount
    fetch('/api/tasks') 
      .then(res => res.json())
      .then(data => setTasks(data));
  }, []);
  
  return (
    <section className="research-tasks">
      <h2>Research Tasks</h2>
      
      {tasks.map(task => (
        <article key={task.id} className="task-item">
          <h3>{task.title}</h3>
          <p>{task.description}</p>
        </article>
      ))}
    </section>
  );
}

export default ResearchTasksList;