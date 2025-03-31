// Generated using webpack-cli https://github.com/webpack/webpack-cli

const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const CopyWebpackPlugin = require('copy-webpack-plugin')

const { resolve } = require('path')

const isProduction = process.env.NODE_ENV == 'production'

const stylesHandler = isProduction ? MiniCssExtractPlugin.loader : 'style-loader'

const config = {
  entry: {
    main: './src/index.ts',
  },
  devtool: 'cheap-source-map',
  output: {
    path: path.resolve(__dirname, 'dist'),
  },
  devServer: {
    static: {
      directory: path.join(__dirname, '/'),
    },
    compress: true,
    port: 4200,
    proxy: [
      {
        context: ['/api'],
        target: 'http://127.0.0.1:8080',
        changeOrigin: true,
        pathRewrite: { '^/api': '' },
      },
    ],
    historyApiFallback: {
      rewrites: [{ from: /^\/$/, to: '/index.html' }],
    },
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './src/index.html',
      filename: 'index.html',
      chunks: ['main'],
    }),
    new CopyWebpackPlugin({
      patterns: [{ from: 'public', to: 'public' }],
    }),

    // Add your plugins here
    // Learn more about plugins from https://webpack.js.org/configuration/plugins/
  ],
  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/i,
        loader: 'ts-loader',
        exclude: ['/node_modules/'],
      },
      {
        test: /\.css$/i,
        include: path.resolve(__dirname, 'src'),
        use: ['style-loader', 'css-loader', 'postcss-loader'],
      },
      {
        test: /\-(template\.html)$/,
        use: [resolve('./', 'src', 'loaders', 'template-loader.js')],
        exclude: /node_modules/,
      },

      // Add your rules for custom modules here
      // Learn more about loaders from https://webpack.js.org/loaders/
    ],
  },
  resolve: {
    extensions: ['.ts', '.js', '.html'],
    alias: {
      lib: resolve('src/lib'),
      components: resolve('src/components'),
      assets: resolve('src/assets'),
      model: resolve('src/model'),
    },
  },
}

module.exports = () => {
  if (isProduction) {
    config.mode = 'production'

    config.plugins.push(new MiniCssExtractPlugin())
  } else {
    config.mode = 'development'
  }
  return config
}
