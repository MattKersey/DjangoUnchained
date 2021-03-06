/* eslint react/prop-types: 0 */
/* istanbul ignore file */
/* global localStorage, fetch, alert, Headers */

import React from 'react'
import { makeStyles, withStyles } from '@material-ui/core/styles'
import clsx from 'clsx'
import Card from '@material-ui/core/Card'
import CardHeader from '@material-ui/core/CardHeader'
import CardMedia from '@material-ui/core/CardMedia'
import CardContent from '@material-ui/core/CardContent'
import CardActions from '@material-ui/core/CardActions'
import Collapse from '@material-ui/core/Collapse'
import IconButton from '@material-ui/core/IconButton'
import Typography from '@material-ui/core/Typography'
import { red } from '@material-ui/core/colors'
import ExpandMoreIcon from '@material-ui/icons/ExpandMore'
import CreateIcon from '@material-ui/icons/Create'
import AddShoppingCartIcon from '@material-ui/icons/AddShoppingCart'
import Dialog from '@material-ui/core/Dialog'
import DialogActions from '@material-ui/core/DialogActions'
import DialogContent from '@material-ui/core/DialogContent'
import DialogTitle from '@material-ui/core/DialogTitle'
import Button from '@material-ui/core/Button'
import TextField from '@material-ui/core/TextField'
import DeleteIcon from '@material-ui/icons/Delete'
import Badge from '@material-ui/core/Badge'
import Box from '@material-ui/core/Box'

const styles = makeStyles((theme) => ({
  root: {
  },
  media: {
    height: 0,
    paddingTop: '56.25%' // 16:9
  },
  expand: {
    transform: 'rotate(0deg)',
    marginLeft: 'auto',
    transition: theme.transitions.create('transform', {
      duration: theme.transitions.duration.shortest
    })
  },
  expandOpen: {
    transform: 'rotate(180deg)'
  },
  avatar: {
    backgroundColor: red[500]
  },
  bruh: {
    backgroundColor: 'blue'
  }
}))

class Product extends React.Component {
  constructor (props) {
    super(props)

    this.state = {
      expanded: false,
      open: false,
      name: '',
      image: '',
      description: '',
      quantity: '',
      price: 0.0,
      original: {},
      deleted: false,
      role: '',
      bulkMin: null,
      bulkPrice: null

    }
    this.handleChange = this.handleChange.bind(this)
  }

  componentDidMount () {
    let bulkMin
    let bulkPrice
    if (this.props.bulkMin > 0) {
      bulkMin = this.props.bulkMin
      bulkPrice = parseFloat(this.props.bulkPrice)
    } else {
      bulkMin = null
      bulkPrice = null
    }
    this.setState({ bulkMin: bulkMin, bulkPrice: bulkPrice, name: this.props.productName, image: this.props.image, description: this.props.description, quantity: this.props.stock, price: this.props.price, role: this.props.role })
    this.setState({ original: { name: this.props.productName, image: this.props.image, description: this.props.description, quantity: this.props.stock, price: this.props.price, role: this.props.role } })
  }

  handleExpandClick (event) {
    console.log(this.state)

    this.setState({ expanded: !this.state.expanded })
  }

  handleOpen () {
    this.setState({ open: true })
  }

  handleClose () {
    this.setState({ open: false })
    this.setState(this.state.original)
  }

  handleChange (event) {
    this.setState({ [event.target.name]: event.target.value })
  }

  handleSubmit (event) {
    const myHeaders = new Headers()
    myHeaders.append('Authorization', 'Bearer ' + localStorage.getItem('token'))
    myHeaders.append('Content-Type', 'application/x-www-form-urlencoded')

    const urlencoded = new URLSearchParams()
    urlencoded.append('name', this.state.name)
    urlencoded.append('image', this.state.image)
    urlencoded.append('stock', parseInt(this.state.quantity))
    urlencoded.append('price', parseFloat(this.state.price))
    urlencoded.append('description', this.state.description)

    const requestOptions = {
      method: 'PUT',
      headers: myHeaders,
      body: urlencoded,
      redirect: 'follow'
    }

    fetch('http://127.0.0.1:8000/api/items/' + this.props.id + '/', requestOptions)
      .then(response => response.json())
      .then(result => { this.setState({ open: false }) })
      .catch(error => alert(error))
    event.preventDefault()
  }

  handleDelete (event) {
    const myHeaders = new Headers()
    myHeaders.append('Authorization', 'Bearer ' + localStorage.getItem('token'))
    myHeaders.append('Content-Type', 'application/x-www-form-urlencoded')

    const urlencoded = new URLSearchParams()
    urlencoded.append('item_id', this.props.id)

    const requestOptions = {
      method: 'POST',
      headers: myHeaders,
      body: urlencoded,
      redirect: 'follow'
    }

    fetch('http://127.0.0.1:8000/api/stores/' + this.props.shopID + '/remove_item/', requestOptions)
      .then(response => response.json())
      .then(result => { window.location.reload() })
      .catch(error => alert(error))
    event.preventDefault()
  }

  render () {
    const { classes } = this.props
    return (
      <div>
        <Badge badgeContent={this.state.bulkMin ? 'Bulk' : null} color='primary'>
          <Card className={classes.root}>
            {(this.state.role === 'Vendor')
              ? <CardHeader
                  action={<IconButton aria-label='settings' onClick={this.handleOpen.bind(this)}> <CreateIcon /></IconButton>}
                  title={this.state.name}
                />
              : <CardHeader title={this.state.name} />}
            <CardMedia
              className={classes.media}
              component='img'
              src={this.state.image}
              title='Image URL'
              height='140'
            />
            <CardActions style={{ justifyContent: 'space-between' }} disableSpacing>
              <IconButton
                className={clsx(classes.expand, { [classes.expandOpen]: this.state.expanded })}
                onClick={this.handleExpandClick.bind(this)}
                aria-expanded={this.state.expanded}
                aria-label='show more'
              >
                <ExpandMoreIcon />
              </IconButton>
              <Box m={1}>
                <Typography paragraph><strong>Quantity </strong>{this.state.quantity} </Typography>
              </Box>
              <Box m={1}>
                <Typography paragraph><strong>Price </strong> ${this.state.price} </Typography>
              </Box>
              <IconButton onClick={this.props.handleAddToCart} aria-label='share'>
                <AddShoppingCartIcon />
              </IconButton>
            </CardActions>
            <Collapse in={this.state.expanded} timeout='auto' unmountOnExit>
              <CardContent>
                <Typography paragraph><strong>Description: </strong> {this.state.description} </Typography>
                {this.state.bulkMin &&
                  <>
                    <Box m={1}>
                      <Typography paragraph><strong>Bulk Minimum: </strong> {this.state.bulkMin} </Typography>
                    </Box>
                    <Box m={1}>
                      <Typography paragraph><strong>Bulk Price </strong> ${this.state.bulkPrice} </Typography>
                    </Box>
                  </>}
              </CardContent>
            </Collapse>
          </Card>
          <Dialog open={this.state.open} onClose={this.handleClose} aria-labelledby='form-dialog-title'>
            <DialogTitle id='form-dialog-title'>Edit {this.state.name}</DialogTitle>
            <DialogContent>
              <TextField
                variant='outlined'
                margin='normal'
                required
                fullWidth
                id='shop_name'
                label='Item Name'
                name='name'
                autoComplete='item_name'
                autoFocus
                value={this.state.name}
                onChange={this.handleChange}
              />
              <TextField
                variant='outlined'
                margin='normal'
                required
                fullWidth
                id='image'
                label='Image URL'
                name='image'
                autoComplete='image'
                value={this.state.image}
                onChange={this.handleChange}
              />
              <TextField
                variant='outlined'
                margin='normal'
                required
                id='description'
                label='Description'
                name='description'
                fullWidth
                autoComplete='description'
                value={this.state.description}
                onChange={this.handleChange}
              />
              <TextField
                variant='outlined'
                margin='normal'
                required
                id='quantity'
                label='Quantity'
                name='quantity'
                autoComplete='quantity'
                autoFocus
                type='number'
                value={this.state.quantity}
                onChange={this.handleChange}
              />

              <TextField
                variant='outlined'
                margin='normal'
                required
                id='price'
                label='Price'
                name='price'
                autoComplete='price'
                value={this.state.price}
                onChange={this.handleChange}
              />
            </DialogContent>
            <DialogActions>
              <Button onClick={this.handleClose.bind(this)} color='primary'>
                Cancel
              </Button>
              <Button
                variant='contained'
                color='secondary'
                className={classes.button}
                startIcon={<DeleteIcon />}
                onClick={this.handleDelete.bind(this)}
              >
                Delete
              </Button>
              <Button
                variant='contained'
                color='primary'
                className={classes.button}
                onClick={this.handleSubmit.bind(this)}
              >
                Confirm
              </Button>
            </DialogActions>
          </Dialog>
        </Badge>
      </div>
    )
  }
}

export default withStyles(styles, { withTheme: true })(Product)
