/* global localStorage */
import React from 'react'
import Avatar from '@material-ui/core/Avatar'
import CssBaseline from '@material-ui/core/CssBaseline'
import Link from '@material-ui/core/Link'
import Box from '@material-ui/core/Box'
import LockOutlinedIcon from '@material-ui/icons/LockOutlined'
import Typography from '@material-ui/core/Typography'
import { withStyles } from '@material-ui/core/styles'
import Container from '@material-ui/core/Container'
import PropTypes from 'prop-types'
import GoogleLogin from 'react-google-login'
import googleLogin from './loginGoogle.js'

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

class Login extends React.Component {
  constructor (props) {
    super(props)

    this.state = {
      username: '',
      password: '',
      error: false
    }
  }

  handleResponse (res) {
    if (res.status === 200) {
      localStorage.setItem('token', res.data.key)
      window.location = '/'
    }
  }

  render () {
    const { classes } = this.props
    const responseGoogle = async (response) => {
      const res = await googleLogin(response.accessToken)
      this.handleResponse(res)
    }
    return (
      <Container component='main' maxWidth='xs'>
        <CssBaseline />
        <div className={classes.paper}>
          <Avatar className={classes.avatar}>
            <LockOutlinedIcon />
          </Avatar>
          <Typography component='h1' variant='h5'>
            Sign into your PyMarket Account
          </Typography>
          <GoogleLogin
            clientId='1099310677669-4lsl049eq46fe9tpct8ro6em04rcm0n1.apps.googleusercontent.com'
            buttonText='LOGIN WITH GOOGLE'
            onSuccess={responseGoogle}
            onFailure={responseGoogle}
          />
        </div>
        <Box mt={8}>
          <Copyright />
        </Box>
      </Container>
    )
  }
}

Login.propTypes = {
  classes: PropTypes.any
}

export default withStyles(styles, { withTheme: true })(Login)
