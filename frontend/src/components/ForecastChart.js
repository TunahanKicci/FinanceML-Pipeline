// frontend/src/components/ForecastChart.js
import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const ForecastChart = ({ forecastData }) => {
  if (!forecastData) return null;

  const { historical, forecast, statistics } = forecastData;

  // Combine historical and forecast data
  const allDates = [...historical.dates, ...forecast.dates];
  const historicalPrices = [...historical.prices, ...Array(forecast.dates.length).fill(null)];
  const forecastPrices = [...Array(historical.dates.length).fill(null), ...forecast.prices];
  
  // Confidence bands (upper/lower)
  const upperBand = forecast.prices.map((price, idx) => 
    price * (1 + (1 - forecast.confidence[idx]) * 0.05)
  );
  const lowerBand = forecast.prices.map((price, idx) => 
    price * (1 - (1 - forecast.confidence[idx]) * 0.05)
  );

  const data = {
    labels: allDates,
    datasets: [
      {
        label: 'Historical Price',
        data: historicalPrices,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        borderWidth: 2,
        pointRadius: 2,
        tension: 0.1
      },
      {
        label: 'Forecast',
        data: forecastPrices,
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        borderWidth: 2,
        borderDash: [5, 5],
        pointRadius: 3,
        tension: 0.1
      },
      {
        label: 'Upper Bound',
        data: [...Array(historical.dates.length).fill(null), ...upperBand],
        borderColor: 'rgba(255, 99, 132, 0.3)',
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        borderWidth: 1,
        borderDash: [2, 2],
        pointRadius: 0,
        fill: '+1'
      },
      {
        label: 'Lower Bound',
        data: [...Array(historical.dates.length).fill(null), ...lowerBand],
        borderColor: 'rgba(255, 99, 132, 0.3)',
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        borderWidth: 1,
        borderDash: [2, 2],
        pointRadius: 0,
        fill: false
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `${forecastData.symbol} - ${forecastData.forecast_days} Day Forecast`,
        font: {
          size: 16,
          weight: 'bold'
        }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += '$' + context.parsed.y.toFixed(2);
            }
            return label;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        ticks: {
          callback: function(value) {
            return '$' + value.toFixed(2);
          }
        }
      },
      x: {
        ticks: {
          maxRotation: 45,
          minRotation: 45
        }
      }
    }
  };

  return (
    <div style={{ height: '500px', width: '100%' }}>
      <Line data={data} options={options} />
      
      <div style={{ marginTop: '20px', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
        <div style={{ padding: '10px', background: '#f3f4f6', borderRadius: '8px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280' }}>Min Price</div>
          <div style={{ fontSize: '18px', fontWeight: 'bold' }}>${statistics.min_price}</div>
        </div>
        <div style={{ padding: '10px', background: '#f3f4f6', borderRadius: '8px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280' }}>Max Price</div>
          <div style={{ fontSize: '18px', fontWeight: 'bold' }}>${statistics.max_price}</div>
        </div>
        <div style={{ padding: '10px', background: '#f3f4f6', borderRadius: '8px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280' }}>Avg Price</div>
          <div style={{ fontSize: '18px', fontWeight: 'bold' }}>${statistics.avg_price}</div>
        </div>
        <div style={{ padding: '10px', background: '#f3f4f6', borderRadius: '8px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280' }}>Volatility</div>
          <div style={{ fontSize: '18px', fontWeight: 'bold' }}>${forecastData.volatility}</div>
        </div>
      </div>
    </div>
  );
};

export default ForecastChart;