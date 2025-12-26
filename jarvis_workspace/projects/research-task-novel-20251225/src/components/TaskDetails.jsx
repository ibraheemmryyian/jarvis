import React, { useState } from 'react';
import './TaskDetails.css';

const TaskDetails = ({ id }) => {
  const [task, setTask] = useState(null);
  
  useEffect(() => {
    // Fetch task details from server on component mount
    fetch(`/api/tasks/${id}`)
      .then(res => res.json())
      .then(data => setTask(data));
  }, [id]);
  
  if (!task) return <div>Loading...</div>;
  
  return (
    <section className="task-details">
      <h1>{task.title}</h1>
      <p>{task.description}</p>
      
      {/* Add more task details */}
    </section>
  );
}

export default TaskDetails;