/* global localStorage */
import React from 'react'
import axios from 'axios'
import Avatar from '@material-ui/core/Avatar'
import CssBaseline from '@material-ui/core/CssBaseline'
import Link from '@material-ui/core/Link'
import Box from '@material-ui/core/Box'
import LockOutlinedIcon from '@material-ui/icons/LockOutlined'
import Typography from '@material-ui/core/Typography'
import { withStyles } from '@material-ui/core/styles'
import Container from '@material-ui/core/Container'
import PropTypes from 'prop-types'

function Copyright () {
  return (
    <Typography variant='body2' color='textSecondary' align='center'>
      {'Copyright © '}
      <Link color='inherit' href='https://material-ui.com/'>
        PyMarket
      </Link>{' '}
      {new Date().getFullYear()}
      .
    </Typography>
  )
}
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
  }
})

class LoginRedirect extends React.Component {
  constructor (props) {
    super(props)
    this.state = {
      token: ''
    }
  }

  componentDidMount () {
    const { location: { search } } = this.props
    console.log(search)
    axios.get('http://127.0.0.1:8000/authredirect/' + search)
      .then((response) => {
        console.log(response.data)
        const newToken = response.data.access_token
        console.log(newToken)
        this.setState({ token: newToken })
        localStorage.setItem('token', newToken)
        window.location = '/'
      })
  }

  render () {
    return null
  }
}

LoginRedirect.propTypes = {
  classes: PropTypes.any,
  location: PropTypes.shape({
    search: PropTypes.any
  })
}

export default withStyles(styles, { withTheme: true })(LoginRedirect)
