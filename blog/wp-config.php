<?php
/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the
 * installation. You don't have to use the web site, you can
 * copy this file to "wp-config.php" and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * MySQL settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://codex.wordpress.org/Editing_wp-config.php
 *
 * @package WordPress
 */

// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define('DB_NAME', 'heroku_46a824368d5b21c');

/** MySQL database username */
define('DB_USER', 'b2ded0004fafa9');

/** MySQL database password */
define('DB_PASSWORD', '01e0a780');

/** MySQL hostname */
define('DB_HOST', 'localhost');

/** Database Charset to use in creating database tables. */
define('DB_CHARSET', 'utf8');

/** The Database Collate type. Don't change this if in doubt. */
define('DB_COLLATE', '');

/**#@+
 * Authentication Unique Keys and Salts.
 *
 * Change these to different unique phrases!
 * You can generate these using the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}
 * You can change these at any point in time to invalidate all existing cookies. This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define('AUTH_KEY',         'o#ZQ3@OD(Si!avyJ77]Ekkmdh|4lS>uqJ^9;OL{#(V`}Dym_6A5H4z1R;Mw>8zg5');
define('SECURE_AUTH_KEY',  'PkbTj:tU;mD~lm!/udYPL.92.4F{UWyc8eLv5Ek<jm_N|}XuWgKz`fn=a3 4ZJwr');
define('LOGGED_IN_KEY',    'kOV5A<0=0I5n+-bT3/KtS}[xDL!@787+D8KA.D rSLmu?}ECXC=5ht(KD^b<3a%V');
define('NONCE_KEY',        '(I*&cfQTiT{`TV%]V0<S]^nd/p$<5%gz]{AG%C.jn3aC23|c6sbO<Z!y$=H(!V-|');
define('AUTH_SALT',        '0MVb2F)[7^sF+iDlXIZSCfPBm-fG($q(-m#A`Q5bO?^@Aw>6wU3A.+?,7@|p^+0,');
define('SECURE_AUTH_SALT', '#J#3(7BpYi0Y %e{c#|,PVX.^;oglSis,4!<-/7lyt@K6>P!%noAhTYClWr96C_c');
define('LOGGED_IN_SALT',   'dB WNL(r+l*Wi(34*m/^b[#;Y)XK/-QQf:~#>@5{m-JbKxu^A+U~-O]UPCY2U+z;');
define('NONCE_SALT',       'GU@Lj>yJi^fGpPilL/Dg]Yb|%F0+!T}BJy+@S+IKTMAXq1<<zooPTkQfkQ{H/?+T');

/**#@-*/

/**
 * WordPress Database Table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix  = 'wp_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the Codex.
 *
 * @link https://codex.wordpress.org/Debugging_in_WordPress
 */
define('WP_DEBUG', false);

/* That's all, stop editing! Happy blogging. */

/** Absolute path to the WordPress directory. */
if ( !defined('ABSPATH') )
	define('ABSPATH', dirname(__FILE__) . '/');

/** Sets up WordPress vars and included files. */
require_once(ABSPATH . 'wp-settings.php');
