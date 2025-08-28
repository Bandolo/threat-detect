# Threat Detection Dashboard

This directory contains code for setting up a visualization dashboard for the threat detection system.

## CloudWatch Dashboard

Run the `create_dashboard.py` script to create a CloudWatch dashboard:

```bash
python create_dashboard.py
```

This will create a dashboard with:
- Lambda function metrics
- Bedrock API usage
- Recent threat detections
- Cost estimates
- S3 object count

## Web Dashboard Setup

To create a web-based dashboard using AWS Amplify:

1. Install Amplify CLI:
```bash
npm install -g @aws-amplify/cli
```

2. Initialize Amplify project:
```bash
mkdir threat-web-dashboard && cd threat-web-dashboard
amplify init --name threat-web-dashboard
```

3. Add API for DynamoDB access:
```bash
amplify add api
# Select REST, DynamoDB, and create a new role
# Create a path /threats with GET method
```

4. Add hosting:
```bash
amplify add hosting
# Select manual deployment
```

5. Deploy:
```bash
amplify publish
```

## Sample React Component

Create a `ThreatDashboard.js` component:

```jsx
import React, { useEffect, useState } from 'react';
import { API } from 'aws-amplify';
import { Bar, Pie } from 'react-chartjs-2';

function ThreatDashboard() {
  const [threats, setThreats] = useState([]);
  
  useEffect(() => {
    fetchThreats();
  }, []);
  
  async function fetchThreats() {
    try {
      const data = await API.get('threatApi', '/threats');
      setThreats(data.Items);
    } catch (err) {
      console.error('Error fetching threats:', err);
    }
  }
  
  // Process data for charts
  const threatsByType = threats.reduce((acc, t) => {
    acc[t.threat] = (acc[t.threat] || 0) + 1;
    return acc;
  }, {});
  
  return (
    <div className="dashboard">
      <h1>Threat Detection Dashboard</h1>
      <div className="charts">
        <div className="chart">
          <h2>Threat Types</h2>
          <Pie 
            data={{
              labels: Object.keys(threatsByType),
              datasets: [{
                data: Object.values(threatsByType),
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
              }]
            }}
          />
        </div>
        <div className="chart">
          <h2>Threat Severity</h2>
          <Bar 
            data={{
              labels: threats.slice(0,10).map(t => t.event_id.substring(0,8)),
              datasets: [{
                label: 'Severity Score',
                data: threats.slice(0,10).map(t => t.anomaly_score),
                backgroundColor: '#36A2EB'
              }]
            }}
          />
        </div>
      </div>
      <div className="recent-threats">
        <h2>Recent Threats</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Time</th>
              <th>Type</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {threats.slice(0,10).map(t => (
              <tr key={t.event_id}>
                <td>{t.event_id.substring(0,8)}</td>
                <td>{new Date(t.timestamp).toLocaleString()}</td>
                <td>{t.threat}</td>
                <td>{t.anomaly_score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ThreatDashboard;
```

## API Lambda Function

Create a Lambda function to fetch threat data from DynamoDB:

```javascript
const AWS = require('aws-sdk');
const docClient = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    const params = {
        TableName: 'ThreatsTable',
        Limit: 100,
        ScanIndexForward: false
    };
    
    try {
        const data = await docClient.scan(params).promise();
        return {
            statusCode: 200,
            headers: {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            },
            body: JSON.stringify(data)
        };
    } catch (err) {
        return {
            statusCode: 500,
            headers: {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            },
            body: JSON.stringify({ error: err.message })
        };
    }
};