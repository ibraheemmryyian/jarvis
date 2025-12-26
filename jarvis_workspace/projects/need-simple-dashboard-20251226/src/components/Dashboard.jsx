import React, { useState, useEffect } from 'react';
import { Grid, Card, Button } from '@material-ui/core';
import { makeStyles } from '@material-ui/styles';

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
  },
  card: {
    padding: theme.spacing(3),
    textAlign: 'center',
  },
}));

function Dashboard() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Grid container spacing={3}>
        {/* Revenue Card */}
        <Grid item xs={12} sm={6} md={4}>
          <Card className={classes.card}>
            <h2>Revenue</h2>
            $1200
          </Card>
        </Grid>

        {/* Users Card */}
        <Grid item xs={12} sm={6} md={4}>
          <Card className={classes.card}>
            <h2>Users</h2>
            10,000
          </Card>
        </Grid>

        {/* Orders Card */}
        <Grid item xs={12} sm={6} md={4}>
          <Card className={classes.card}>
            <h2>Orders</h2>
            500
          </Card>
        </Grid>
      </Grid>
    </div>
  );
}

export default Dashboard;