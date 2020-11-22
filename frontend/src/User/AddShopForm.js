import React from 'react'
import axios from 'axios'
import Avatar from '@material-ui/core/Avatar'
import Button from '@material-ui/core/Button'
import CssBaseline from '@material-ui/core/CssBaseline'
import TextField from '@material-ui/core/TextField'
import LockOutlinedIcon from '@material-ui/icons/LockOutlined'
import Typography from '@material-ui/core/Typography'
import { withStyles } from '@material-ui/core/styles'
import Container from '@material-ui/core/Container'
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
      store_name: '',
      address: '',
      category: ''
    }

    this.handleChange = this.handleChange.bind(this)
    this.handleSubmit = this.handleSubmit.bind(this)
  }

  handleChange (event) {
    this.setState({ [event.target.name]: event.target.value })
  }

  handleSubmit (event) {
    console.log(this.state)
  }

  render () {
    const { classes } = this.props
    return (
      <Container component='main' maxWidth='xs'>
        <CssBaseline />
        <div className={classes.paper}>
          <Avatar className={classes.avatar}>
            <LockOutlinedIcon />
          </Avatar>
          <Typography component='h1' variant='h5'>
            Add a new Store
          </Typography>
          <form className={classes.form} onSubmit={this.handleSubmit.bind(this)}>
            <TextField
              variant='outlined'
              margin='normal'
              required
              fullWidth
              id='shop_name'
              label='Store Name'
              name='shop_name'
              autoComplete='shop_name'
              autoFocus
              onChange={this.handleChange}
            />
            <TextField
              variant='outlined'
              margin='normal'
              required
              fullWidth
              id='address'
              label='Address'
              name='address'
              autoComplete='last_name'
              onChange={this.handleChange}
            />
            <FormControl className={classes.formControl}>
              <InputLabel id='demo-simple-select-label'>Category</InputLabel>
              <Select
                labelId='demo-simple-select-label'
                id='demo-simple-select'
                name='category'
                value={this.state.category}
                onChange={this.handleChange}
              >
                <MenuItem value='Food'>Food</MenuItem>
                <MenuItem value='Clothing'>Clothing</MenuItem>
                <MenuItem value='etc'>etc</MenuItem>
              </Select>
            </FormControl>
            <Button
              type='submit'
              fullWidth
              variant='contained'
              color='primary'
              className={classes.submit}
            >
              Create Store
            </Button>
          </form>
        </div>
      </Container>
    )
  }
}

AddShopForm.propTypes = {
  classes: PropTypes.any
}

export default withRouter(withStyles(styles, { withTheme: true })(AddShopForm))