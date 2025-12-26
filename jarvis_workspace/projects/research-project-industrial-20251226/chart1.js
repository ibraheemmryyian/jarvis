// Code to generate a bar chart comparing material flow efficiency across different industries
import { Bar } from 'react-chartjs-2';
import { Chart, CategoryScale, LinearScale, BarElement } from 'chart.js';

Chart.register(CategoryScale, LinearScale, BarElement);

const data = {
  labels: ['Industry A', 'Industry B', 'Industry C'],
  datasets: [
    {
      label: 'Material Flow Efficiency Score',
      data: [85, 78, 92],
      backgroundColor: 'rgba(255, 99, 132, 0.2)',
      borderColor: 'rgba(255, 99, 132, 1)',
      borderWidth: 1,
    },
  ],
};

const options = {
  scales: {
    y: {
      beginAtZero: true,
      steps: 10,
      stepSize: 10,
      title: {
        display: true,
        text: 'Score',
      },
    },
  },
};

return (
  <div>
    <Bar data={data} options={options} />
  </div>
);