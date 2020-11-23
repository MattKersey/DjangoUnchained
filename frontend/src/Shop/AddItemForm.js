/* global localStorage, fetch, Headers, alert */
/* istanbul ignore file */
/* eslint react/prop-types: 0 */

import React from 'react'
import Button from '@material-ui/core/Button'
import TextField from '@material-ui/core/TextField'
import { withStyles } from '@material-ui/core/styles'
import PropTypes from 'prop-types'
import { withRouter } from 'react-router-dom'
import InputLabel from '@material-ui/core/InputLabel'
import MenuItem from '@material-ui/core/MenuItem'
import FormControl from '@material-ui/core/FormControl'
import Select from '@material-ui/core/Select'

const styles = theme => ({
  paper: {
    marginTop: theme.spacing(8),
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center'
  },
  avatar: {
    margin: theme.spacing(1),
    backgroundColor: theme.palette.secondary.main
  },
  form: {
    width: '100%', // Fix IE 11 issue.
    marginTop: theme.spacing(1)
  },
  submit: {
    margin: theme.spacing(3, 0, 2)
  },
  formControl: {
    margin: theme.spacing(1),
    minWidth: 120
  },
  selectEmpty: {
    marginTop: theme.spacing(2)
  }
})

class AddShopForm extends React.Component {
  constructor (props) {
    super(props)

    this.state = {
      item_name: '',
      stock: 0,
      price: 0,
      type: '',
      bulkMin: 0,
      bulkPrice: 0.0,
      description: ''
    }

    this.handleChange = this.handleChange.bind(this)
    this.handleSubmit = this.handleSubmit.bind(this)
  }

  handleChange (event) {
    this.setState({ [event.target.name]: event.target.value })
  }

  handleSubmit (event) {
    const myHeaders = new Headers()
    myHeaders.append('Authorization', 'Bearer ' + localStorage.getItem('token'))
    myHeaders.append('Content-Type', 'application/x-www-form-urlencoded')

    const urlencoded = new URLSearchParams()
    urlencoded.append('store_id', parseInt(this.props.match.params.shopID))
    urlencoded.append('name', this.state.item_name)
    urlencoded.append('stock', parseInt(this.state.stock))
    urlencoded.append('price', parseFloat(this.state.price))
    urlencoded.append('orderType', this.state.type)
    urlencoded.append('bulkMinimum', parseInt(this.state.bulkMin))
    urlencoded.append('bulkPrice', parseFloat(this.state.bulkPrice))
    urlencoded.append('description', this.state.description)

    const requestOptions = {
      method: 'POST',
      headers: myHeaders,
      body: urlencoded,
      redirect: 'follow'
    }

    fetch('http://127.0.0.1:8000/api/items/', requestOptions)
      .then(response => response.json())
      .then(result => { window.location.reload() })
      .catch(error => alert(error))
    event.preventDefault()
  }

  render () {
    const { classes } = this.props
    return (
      <div>
        <form className={classes.form} onSubmit={this.handleSubmit.bind(this)}>
          <TextField
            variant='outlined'
            margin='normal'
            required
            fullWidth
            id='shop_name'
            label='Item Name'
            name='item_name'
            autoComplete='item_name'
            autoFocus
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
            onChange={this.handleChange}
          />

          <TextField
            variant='outlined'
            margin='normal'
            required
            id='stock'
            label='Stock'
            name='stock'
            autoComplete='stock'
            autoFocus
            onChange={this.handleChange}
          />

          <TextField
            variant='outlined'
            margin='normal'
            required
            id='stock'
            label='Price'
            name='price'
            autoComplete='price'
            onChange={this.handleChange}
          />
          <FormControl className={classes.formControl}>
            <InputLabel id='demo-simple-select-label'>Type</InputLabel>
            <Select
              labelId='demo-simple-select-label'
              id='demo-simple-select'
              name='type'
              value={this.state.type}
              onChange={this.handleChange}
            >
              <MenuItem value='Individual'>Individual</MenuItem>
              <MenuItem value='Bulk'>Bulk</MenuItem>
              <MenuItem value='Both'>Both</MenuItem>
            </Select>
          </FormControl>
          {((this.state.type === 'Bulk') || (this.state.type === 'Both')) ? <div><TextField variant='outlined' margin='normal' required id='bulkMin' label='Bulk Min.' name='bulkMin' autoComplete='Bulk Min' onChange={this.handleChange} /> <TextField variant='outlined' margin='normal' required id='Bulk Price' label='Bulk Price' name='bulkPrice' autoComplete='Bulk Min' onChange={this.handleChange} /> </div> : null}

          <Button
            type='submit'
            fullWidth
            variant='contained'
            color='primary'
            className={classes.submit}
          >
            Add Item
          </Button>
        </form>
      </div>
    )
  }
}

AddShopForm.propTypes = {
  classes: PropTypes.any
}

export default withRouter(withStyles(styles, { withTheme: true })(AddShopForm))
