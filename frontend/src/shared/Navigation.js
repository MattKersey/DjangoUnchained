/* eslint react/prop-types: 0 */
import React from 'react'
import './navigation.css'
import { makeStyles, withStyles } from '@material-ui/core/styles'
import AppBar from '@material-ui/core/AppBar'
import Toolbar from '@material-ui/core/Toolbar'
import Button from '@material-ui/core/Button'
import Typography from '@material-ui/core/Typography'
import ExitToAppIcon from '@material-ui/icons/ExitToApp'
import Link from '@material-ui/core/Link'
import PropTypes from 'prop-types'

const styles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
    marginBottom: theme.spacing(2)
  },
  menuButton: {
    marginRight: theme.spacing(2)
  }
}))

class NavBar extends React.Component {
  /* istanbul ignore next */
  render () {
    const { classes } = this.props
    return (
      <div className={classes.root}>
        <AppBar position='static'>
          <Toolbar>
            <Typography variant='h6' noWrap>
              <Link href='/' data-testid='title' className='title' onClick={(event) => event.preventDefault}>
                PyMarket
              </Link>
            </Typography>
            {this.props.isLogged ? <Button to='/' onClick={this.props.handleLogOut} color='inherit'><ExitToAppIcon /></Button> : null}
          </Toolbar>
        </AppBar>
      </div>
    )
  }
}
NavBar.propTypes = {
  classes: PropTypes.any
}
export default withStyles(styles, { withTheme: true })(NavBar)
