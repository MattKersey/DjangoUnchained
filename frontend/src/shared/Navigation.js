import React from 'react'
import './navigation.css'
import { makeStyles, withStyles } from '@material-ui/core/styles'
import AppBar from '@material-ui/core/AppBar'
import Toolbar from '@material-ui/core/Toolbar'
import Button from '@material-ui/core/Button'
import Typography from '@material-ui/core/Typography'
import ExitToAppIcon from '@material-ui/icons/ExitToApp'
const styles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
    marginBottom: theme.spacing(2)
  },
  menuButton: {
    marginRight: theme.spacing(2)
  },
  title: {
    flexGrow: 1
  }
}))

class NavBar extends React.Component {
  constructor (props) {
    super(props)

    console.log(this.props)
  }

  render () {
    const { classes } = this.props
    return (
      <div className={classes.root}>
        <AppBar position='static'>
          <Toolbar display='flex' justifyContent='space-between'>
            <Typography variant='h6' noWrap>
              PyMarket
            </Typography>
            {this.props.isLogged ? <Button to='/' onClick={this.props.handleLogOut} color='inherit'><ExitToAppIcon /></Button> : null}
          </Toolbar>
        </AppBar>
      </div>
    )
  }
}

export default withStyles(styles, { withTheme: true })(NavBar)
