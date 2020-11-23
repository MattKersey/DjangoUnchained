/* global localStorage, fetch */
/* istanbul ignore file */

import React from 'react'
import Product from './Product'
import Grid from '@material-ui/core/Grid'
import Typography from '@material-ui/core/Typography'
import Table from '@material-ui/core/Table'
import TableBody from '@material-ui/core/TableBody'
import TableCell from '@material-ui/core/TableCell'
import TableContainer from '@material-ui/core/TableContainer'
import TableHead from '@material-ui/core/TableHead'
import TableRow from '@material-ui/core/TableRow'
import Paper from '@material-ui/core/Paper'
import Fab from '@material-ui/core/Fab'
import AddIcon from '@material-ui/icons/Add'
import Box from '@material-ui/core/Box'
import Button from '@material-ui/core/Button'
import Dialog from '@material-ui/core/Dialog'
import DialogActions from '@material-ui/core/DialogActions'
import DialogContent from '@material-ui/core/DialogContent'
import DialogContentText from '@material-ui/core/DialogContentText'
import DialogTitle from '@material-ui/core/DialogTitle'
import AddItemForm from './AddItemForm.js'
import ShoppingCartIcon from '@material-ui/icons/ShoppingCart'

class Shop extends React.Component {
  constructor (props) {
    super(props)

    this.state = {
      products: {},
      inCart: {},
      storeName: '',
      open: false,
      store_id: -1
    }
  }

  onAddToCart (event, data) {
    if (data.pk in this.state.inCart) {
      const newProd = { quantity: this.state.inCart[data.pk].quantity + 1, productName: data.name, product: data, price: data.price }
      const oldCart = this.state.inCart
      oldCart[data.pk] = newProd
      this.setState({ inCart: oldCart })
    } else {
      const newProd = { quantity: 1, productName: data.name, product_meta: data, price: data.price }
      const oldCart = this.state.inCart
      oldCart[data.pk] = newProd
      this.setState({ inCart: oldCart })
      // TODO: UPDATE PRODUCTS STATE SO IT SUBTRRACTS FROM THE VIEW
    }
  }

  componentDidMount () {
    const storeID = this.props.match.params.shopID
    fetch('http://127.0.0.1:8000/api/stores/' + storeID + '/', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    })
      .then(res => res.json())
      .then(json => {
        console.log(json.items)
        const productElements = {}
        for (let i = 0; i < json.items.length; i++) {
          productElements[json.items[i].pk] = <Grid item key={json.items[i].pk} md={3}><Product className='product' handleAddToCart={(event) => this.onAddToCart(event, json.items[i], i)} stock={json.items[i].stock} description={json.items[i].description} productName={json.items[i].name} price={json.items[i].price} imageURL={json.items[i].image} /></Grid>
        }
        this.setState({ products: productElements, storeName: "Carlos' Magcal Emporium", store_id: storeID })
      })
  }

  handleOpen () {
    this.setState({ open: true })
  }

  handleClose () {
    this.setState({ open: false })
  }

  render () {
    return (
      <div>
        <Typography component='h1' variant='h5'>
          {this.state.storeName}
        </Typography>
        <Box align='center'>
          <Grid container direction='row' justify='flex-start' alignItems='baseline' spacing={10}>
            {Object.values(this.state.products)}
          </Grid>
          <br />
          <Fab color='primary' onClick={this.handleOpen.bind(this)} aria-label='add' variant='extended'>
            <AddIcon />
            Add an Item
          </Fab>
        </Box>
        <br />
        <Typography component='h1' variant='h5'>
          Cart <ShoppingCartIcon />
        </Typography>
        <TableContainer component={Paper}>
          <Table aria-label='simple table'>
            <TableHead>
              <TableRow>
                <TableCell>Item Name</TableCell>
                <TableCell align='right'>Quantity</TableCell>
                <TableCell align='right'>Price</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {Object.keys(this.state.inCart).map((product) => (
                <TableRow key={this.state.inCart[product].productName}>
                  <TableCell component='th' scope='row'>
                    {this.state.inCart[product].productName}
                  </TableCell>
                  <TableCell align='right'>{this.state.inCart[product].quantity}</TableCell>
                  <TableCell align='right'>{this.state.inCart[product].price}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <Dialog open={this.state.open} onClose={this.handleClose} aria-labelledby='form-dialog-title'>
          <DialogTitle id='form-dialog-title'>Add an Item</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Fill out the following form to create an item
            </DialogContentText>
            <AddItemForm />
          </DialogContent>
          <DialogActions>
            <Button onClick={this.handleClose.bind(this)} color='primary'>
              Cancel
            </Button>
          </DialogActions>
        </Dialog>
      </div>
    )
  }
}

export default Shop
