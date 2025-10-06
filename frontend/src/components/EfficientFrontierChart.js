// frontend/src/components/EfficientFrontierChart.js
import React from 'react';
import { Scatter } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

const EfficientFrontierChart = ({ data }) => {
  if (!data || !data.efficient_frontier) return null;

  const { efficient_frontier, max_sharpe_portfolio, min_variance_portfolio, asset_statistics } = data;

  // Prepare data for scatter plot
  const chartData = {
    datasets: [
      // Efficient Frontier Line
      {
        label: 'Efficient Frontier',
        data: efficient_frontier.volatilities.map((vol, idx) => ({
          x: vol * 100,
          y: efficient_frontier.returns[idx] * 100
        })),
        borderColor: 'rgb(102, 126, 234)',
        backgroundColor: 'rgba(102, 126, 234, 0.5)',
        showLine: true,
        pointRadius: 3,
        pointHoverRadius: 5,
        borderWidth: 3
      },
      // Max Sharpe Portfolio
      {
        label: 'Max Sharpe Portfolio',
        data: [{
          x: max_sharpe_portfolio.volatility * 100,
          y: max_sharpe_portfolio.expected_return * 100
        }],
        backgroundColor: 'rgb(16, 185, 129)',
        borderColor: 'rgb(16, 185, 129)',
        pointRadius: 10,
        pointHoverRadius: 12,
        pointStyle: 'star'
      },
      // Min Variance Portfolio
      {
        label: 'Min Variance Portfolio',
        data: [{
          x: min_variance_portfolio.volatility * 100,
          y: min_variance_portfolio.expected_return * 100
        }],
        backgroundColor: 'rgb(59, 130, 246)',
        borderColor: 'rgb(59, 130, 246)',
        pointRadius: 10,
        pointHoverRadius: 12,
        pointStyle: 'triangle'
      },
      // Individual Assets
      {
        label: 'Individual Assets',
        data: asset_statistics.map(asset => ({
          x: asset.volatility * 100,
          y: asset.expected_return * 100,
          label: asset.symbol
        })),
        backgroundColor: 'rgba(239, 68, 68, 0.6)',
        borderColor: 'rgb(239, 68, 68)',
        pointRadius: 8,
        pointHoverRadius: 10
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 15,
          font: {
            size: 12
          }
        }
      },
      title: {
        display: true,
        text: 'Efficient Frontier - Risk vs Return',
        font: {
          size: 16,
          weight: 'bold'
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const dataset = context.dataset.label;
            const point = context.raw;
            
            if (point.label) {
              return `${point.label}: Return ${point.y.toFixed(2)}%, Risk ${point.x.toFixed(2)}%`;
            }
            
            return `${dataset}: Return ${point.y.toFixed(2)}%, Risk ${point.x.toFixed(2)}%`;
          }
        }
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Volatility (Risk) %',
          font: {
            size: 14,
            weight: 'bold'
          }
        },
        ticks: {
          callback: function(value) {
            return value.toFixed(1) + '%';
          }
        }
      },
      y: {
        title: {
          display: true,
          text: 'Expected Return %',
          font: {
            size: 14,
            weight: 'bold'
          }
        },
        ticks: {
          callback: function(value) {
            return value.toFixed(1) + '%';
          }
        }
      }
    }
  };

  return (
    <div style={{ height: '500px', width: '100%' }}>
      <Scatter data={chartData} options={options} />
      
      <div style={{ 
        marginTop: '20px', 
        padding: '15px', 
        background: '#f9fafb', 
        borderRadius: '8px',
        fontSize: '14px',
        color: '#6b7280'
      }}>
        <strong>How to read this chart:</strong>
        <ul style={{ marginTop: '10px', marginBottom: 0, paddingLeft: '20px' }}>
          <li>The blue line shows the efficient frontier - optimal portfolios for each risk level</li>
          <li>Green star: Maximum Sharpe ratio (best risk-adjusted return)</li>
          <li>Blue triangle: Minimum variance (lowest risk)</li>
          <li>Red dots: Individual assets (not optimized)</li>
          <li>Points above the line are theoretically impossible</li>
          <li>Points below the line are sub-optimal</li>
        </ul>
      </div>
    </div>
  );
};

export default EfficientFrontierChart;