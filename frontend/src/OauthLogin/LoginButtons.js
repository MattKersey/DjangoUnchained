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

class OauthLogin extends React.Component {
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
            Sign into your PyMarket Account
          </Typography>
          <Link color='inherit' href='http://127.0.0.1:8000/o/authorize/?response_type=code&client_id=naKKnrr5KL3QISISbdM2XPYlou0HkiVJucMCMyKI&redirect_uri=http://localhost:1234/loginredirect'>
            Login with OAuth
          </Link>{' '}
        </div>
        <Box mt={8}>
          <Copyright />
        </Box>
      </Container>
    )
  }
}

OauthLogin.propTypes = {
  classes: PropTypes.any
}

export default withStyles(styles, { withTheme: true })(OauthLogin)
