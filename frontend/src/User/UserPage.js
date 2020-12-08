/* global localStorage */

import React from 'react'
import StoreCard from './StoreCard'
import Grid from '@material-ui/core/Grid'
import Fab from '@material-ui/core/Fab'
import AddIcon from '@material-ui/icons/Add'
import Typography from '@material-ui/core/Typography'
import axios from 'axios'
import Box from '@material-ui/core/Box'
import Dialog from '@material-ui/core/Dialog'
import DialogActions from '@material-ui/core/DialogActions'
import DialogContent from '@material-ui/core/DialogContent'
import DialogContentText from '@material-ui/core/DialogContentText'
import DialogTitle from '@material-ui/core/DialogTitle'
import Button from '@material-ui/core/Button'
import AddShopForm from './AddShopForm.js'
import PropTypes from 'prop-types'

import './home.css'
class UserPage extends React.Component {
  constructor (props) {
    super(props)
    this.state = {
      email: '',
      shops: [],
      open: false
    }
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

  handleOpen () {
    this.setState({ open: true })
  }

  handleClose () {
    this.setState({ open: false })
  }

  handleSub (event) {
    this.setState({ open: false })
    this.props.onSub()
  }

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
        <Box mt={2} minWidth='400' minHeight='100' className='shopContainer'>
          <Grid
            container direction='row' justify='space-evenly'
            alignItems='center' spacing={10}
          >
            {this.state.shops.map((shop, index) =>
              <Grid item key={index} xs={12} md={4}>
                <StoreCard name={shop.store_name} role={shop.role} address={shop.store_address} category={shop.store_category} id={shop.store_id} />
              </Grid>
            )}
          </Grid>
        </Box>
        <Box>
          <Fab color='primary' data-testid='openModal' onClick={this.handleOpen.bind(this)} aria-label='add'>
            <AddIcon />
          </Fab>
        </Box>
        <Dialog open={this.state.open} onClose={this.handleClose} aria-labelledby='form-dialog-title'>
          <DialogTitle id='form-dialog-title'>Create a Store</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Fill out the following form to create an item
            </DialogContentText>
            <AddShopForm onSub={(event) => this.handleSub(event)} />
          </DialogContent>
          <DialogActions>
            <Button data-testid='close' onClick={this.handleClose.bind(this)} color='primary'>
              Cancel
            </Button>
          </DialogActions>
        </Dialog>

      </div>
    )
  }
}

UserPage.propTypes = {
  onSub: PropTypes.any
}

export default UserPage
