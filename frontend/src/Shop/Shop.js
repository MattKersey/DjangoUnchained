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
class Shop extends React.Component {
  constructor (props) {
    super(props)

    this.state = {
      products: [],
      inCart: {},
      storeName: ''
    }
  }

  onAddToCart (event, data) {
    if (data.SKU in this.state.inCart) {
      const newProd = { quantity: this.state.inCart[data.SKU].quantity + 1, productName: data.productName, product: data, price: data.productPrice }
      const oldCart = this.state.inCart
      oldCart[data.SKU] = newProd
      this.setState({ inCart: oldCart })
    } else {
      const newProd = { quantity: 1, productName: data.productName, product_meta: data, price: data.productPrice }
      const oldCart = this.state.inCart
      oldCart[data.SKU] = newProd
      this.setState({ inCart: oldCart })
    }
  }

  componentDidMount () {
    const fakeData = [{ productName: 'Test1', productPrice: 3.99, imageURL: 'https://picsum.photos/200/300', SKU: 123 },
      { productName: 'Test2', productPrice: 3.99, imageURL: 'https://picsum.photos/200/300', SKU: 132 },
      { productName: 'Test3', productPrice: 3.99, imageURL: 'https://picsum.photos/200/300', SKU: 1234 },
      { productName: 'Test4', productPrice: 3.99, imageURL: 'https://picsum.photos/200/300', SKU: 123424 },
      { productName: 'Test5', productPrice: 3.99, imageURL: 'https://picsum.photos/200/300', SKU: 12343354 },
      { productName: 'Test6', productPrice: 3.99, imageURL: 'https://picsum.photos/200/300', SKU: 12345435 },
      { productName: 'Test7', productPrice: 3.99, imageURL: 'https://picsum.photos/200/300', SKU: 12345545 },
      { productName: 'Test8', productPrice: 3.99, imageURL: 'https://picsum.photos/200/300', SKU: 1234545454 }]
    // Fetch Data HERE
    const productElements = []
    for (let i = 0; i < fakeData.length; i++) {
      productElements.push(<Grid item key={fakeData[i].SKU} md={3}><Product className='product' handleAddToCart={(event) => this.onAddToCart(event, fakeData[i])} productName={fakeData[i].productName} price={fakeData[i].productPrice} imageURL={fakeData[i].imageURL} /></Grid>)
    }
    this.setState({ products: productElements, storeName: "Carlos' Magcal Emporium" })
  }

  render () {
    return (
      <div>
        <Typography component='h1' variant='h5'>
          {this.state.storeName}
        </Typography>
        <Grid container direction='row' justify='space-evenly' alignItems='baseline' spacing={10}>
          {this.state.products}
        </Grid>
        <br />
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
      </div>
    )
  }
}

export default Shop
