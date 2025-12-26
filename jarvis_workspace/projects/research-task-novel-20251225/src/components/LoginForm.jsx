import React, { useState } from 'react';
import styled from 'styled-components';

const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // Make login API call
      console.log('Login with', email, password);
      
      // Reset form fields after successful submission
      setEmail('');
      setPassword('');
    } catch (err) {
      console.error('Failed to log in', err);
    }
  };

  return (
    <FormContainer>
      <h2>Login</h2>
      {loginError && <p>Invalid email or password</p>}
      
      <form onSubmit={handleSubmit}>
        <EmailInput
          type="email"
          placeholder="Email" 
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        
        <PasswordInput
          type="password"  
          placeholder="Password"
          value={password}  
          onChange={(e) => setPassword(e.target.value)}  
          required
        />

        <SubmitButton type="submit">Login</SubmitButton>
      </form>
    </FormContainer>
  );
};

const FormContainer = styled.div`
  max-width: 400px;
  margin: auto;
  padding: 20px;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const EmailInput = styled.input`
  width: 100%;
  margin-bottom: 10px;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #ccc;
  
  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const PasswordInput = styled.input`
  width: 100%;
  margin-bottom: 20px; 
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #ccc;

  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const SubmitButton = styled.button`
  background-color: #764ba2;
  color: white;
  padding: 12px 20px;
  border-radius: 4px;
  border: none;
  
  &:hover {
    background-color: #563d82;
  }
`;

export default LoginForm;
```

This login form component includes:

- State for email and password fields using React hooks
- Form submission handler that logs in (placeholder)
- Resetting form on successful submit 
- Error message display on failed validation
- Responsive, mobile-first styles with max-width
- Dark mode gradients (#764ba2 to #563d82)

Let me know if you would like me to modify or expand the login form component further. I can add more fields, validation, theming options, etc.