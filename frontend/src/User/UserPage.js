/* global localStorage */

import React from 'react'
import StoreCard from './StoreCard'
import Grid from '@material-ui/core/Grid'
import Fab from '@material-ui/core/Fab'
import AddIcon from '@material-ui/icons/Add'
import Typography from '@material-ui/core/Typography'
import axios from 'axios'
import Box from '@material-ui/core/Box'
import './home.css'
class UserPage extends React.Component {
  constructor (props) {
    super(props)
    this.state = { email: '', shops: [] }
  }

  componentDidMount () {
    axios.get('http://127.0.0.1:8000/api/users/current_user/', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
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

  handleAddStore () { window.location = '/register_shop' }

  render () {
    return (
      <div align='center'>
        <Box mb={4} mt={2}>
          <Typography component='h1' variant='h5'>
            Welcome {this.state.email}!
          </Typography>
          <Typography component='h1' variant='h5'>
            Your Stores:
          </Typography>
        </Box>
        <Box mt={2} minHeight='100' className='shopContainer'>
          <Grid container direction='row' alignItems='baseline' spacing={10}>
            {this.state.shops.map((shop, index) =>
              <Grid item key={index} md={3}>
                <StoreCard name={shop.store_name} id={shop.store_id} />
              </Grid>
            )}
          </Grid>
        </Box>
        <Box>
          <Fab color='primary' onClick={this.handleAddStore} aria-label='add'>
            <AddIcon />
          </Fab>
        </Box>

      </div>
    )
  }
}

export default UserPage
