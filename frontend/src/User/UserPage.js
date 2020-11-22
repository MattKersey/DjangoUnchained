/* global localStorage */

import React from 'react'
import StoreCard from './StoreCard'
import Grid from '@material-ui/core/Grid'
import Fab from '@material-ui/core/Fab'
import AddIcon from '@material-ui/icons/Add'
import Typography from '@material-ui/core/Typography'
import axios from 'axios'
import Box from '@material-ui/core/Box'
class UserPage extends React.Component {
  constructor (props) {
    super(props)
    this.state = { email: '', shops: [] }
  }

  componentDidMount () {
    axios.get('http://localhost:8000/api/current_user/', {
      headers: {
        Authorization: `Token ${localStorage.getItem('token')}`
      }
    })
      .then((res) => {
        this.setState({ email: res.data.email, shops: res.data.stores })
        console.log(res.data.stores)
      })
      .catch((error) => {
        console.error(error)
      })
  }

  render () {
    return (
      <div align='center'>
        <Box mb={4}>
          <Typography component='h1' variant='h5' mb={2}>
            Welcome {this.state.email}!
          </Typography>
        </Box>
        <Grid container direction='row' alignItems='baseline' spacing={10}>
          {this.state.shops.map((shop, index) =>
            <Grid item key={index} md={3}>
              <StoreCard name={shop.store_name} id={shop.store_id} />
            </Grid>
          )}
          <Grid item md={3}>
            <Fab color='primary' aria-label='add' variant='extended'>
              <AddIcon />
              Add Store
            </Fab>
          </Grid>
        </Grid>

      </div>
    )
  }
}

export default UserPage