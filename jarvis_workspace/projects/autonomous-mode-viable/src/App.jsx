// OnboardingFlow.jsx (updated)
const OnboardingFlow = () => {
  // ...

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  // ...
};