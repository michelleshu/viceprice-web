<?php
define( '_MAILCHIMP_APIKEY', 'd9b9f506552fc7ea1bd19c7e6e5fcd1a-us12' ); // ADD YOUR MAILCHIMP API KEY
define( '_MAILCHIMP_LISTID', '04bd9d748e' ); // ADD YOUR MAILCHIMP LIST ID
define( '_EMAIL', 'justin@viceprice.co' ); // SPECIFY YOUR OWN EMAIL ADDRESS
$special_header = 'false'; // SET IT TO 'false' IF YOU HAVE ANY ISSUES WITH GETTING THE NOTIFICATION EMAIL IN 'mail' OR 'mixed' MODE
if( isset( $_SERVER['HTTP_X_REQUESTED_WITH'] ) && ( $_SERVER['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest' ) ) {
$result = false;
	if ( isset( $_REQUEST[ 'action' ] ) ) {
		if ( $_REQUEST[ 'action' ] == "subscription_signup" ) {
			if ( isset( $_REQUEST[ 'email' ] ) ) {
				$mail = $_REQUEST[ 'email' ];
			}
			if ( ! filter_var( $mail, FILTER_VALIDATE_EMAIL ) ) {
				print( 'Error: Invalid Email Address' );
			}
			else {
			if ( $_REQUEST[ 'mode' ] == 'mailchimp' || $_REQUEST[ 'mode' ] == 'mixed' ) {
				require_once( 'MailChimp.php' );
				$MailChimp = new MailChimp( _MAILCHIMP_APIKEY );
				if ( $_REQUEST[ 'mailchimp_listid' ] != false ) {
					$mlid = _MAILCHIMP_LISTID;
				}
				else {
					$mlid = $_REQUEST[ 'mailchimp_listid' ];
				}
				if ( ! empty( $_REQUEST[ 'customfieldsarray' ] ) ) {
					foreach( $_REQUEST[ 'customfieldsarray' ] as $cfa ) {
						$mv[ $cfa ] = $_REQUEST[ $cfa ];
						$customfields .='
	'.$cfa.': '.$_REQUEST[ $cfa ]; 
					}
				}
				$mc_data = array(
					'email_address' => $_REQUEST[ 'email' ]
				);
				if ( ! empty( $mv ) ) {
					$mc_data[ 'merge_fields' ] = $mv;
				}
				if ( $_REQUEST[ 'double_optin' ] == true ) {
					$mc_data[ 'status' ] = 'subscribed';
				}
				else {
					$mc_data[ 'status' ] = 'pending';
				}
				$result = $MailChimp->post( 'lists/' . $mlid . '/members', $mc_data );
				if ( $result[ 'status' ] == 400 && $_REQUEST[ 'update_existing' ] == true ) {
					$subscriber_hash = $MailChimp->subscriberHash( $_REQUEST[ 'email' ] );
					$result = $MailChimp->patch( 'lists/' . $mlid . '/members/' . $subscriber_hash, $mc_data );					
				}
				if ( $MailChimp->success() ) {
					$result = true;
				}
				else {
					$result = false;
					echo $MailChimp->getLastError();
				}
			}
			if ( $_REQUEST[ 'mode' ] == 'mail' || $_REQUEST[ 'mode' ] == 'mixed' ) {
				if ( $_REQUEST[ 'mode' ] == 'mail' && ! empty( $_REQUEST[ 'customfieldsarray' ] ) && empty( $customfields ) ) {
					if ( ! empty( $_REQUEST[ 'customfieldsarray' ] ) ) {
						foreach( $_REQUEST[ 'customfieldsarray' ] as $cfa ) {
							$mv[ $cfa ] = $_REQUEST[ $cfa ];
							$customfields .='
' . $cfa . ': ' . $_REQUEST[ $cfa ]; 
						}
					}	
				}
				if ( ! filter_var( _EMAIL ) ) {
					print( 'Error: Invalid Recipient Email' );
					die();
				}
				$body = "You've got a new signup on the http://" . $_SERVER[ 'HTTP_HOST' ] . str_replace( '/php/handler.php', '', $_SERVER[ 'HTTP_REFERRER' ] ) . " website with the following mail address: " . $mail . $customfields . "
				
				";
				$from_a = 'noreply@' . str_replace( "www.", "", $_SERVER[ 'HTTP_HOST' ] );
				$from_name = 'Simple Signup Form';
				$header = 'MIME-Version: 1.0' . '\r\n';
				$header .= 'From: "' . $from_name . '" <' . $from_a . '>\r\n';
				$header .= 'Content-type: text/plain; charset=UTF-8' . '\r\n';
				if ( $special_header == 'true' ) {
					if ( mail( _EMAIL, 'Subscription Signup', $body, $header, "-f" . $from_a ) ) {
						$result = true;
					}
					else {
						$result = false;
					}
				}
				else {
					if ( mail( _EMAIL, 'Subscription Signup', $body, $header ) ) {
						$result = true;
					}
					else {
						$result = false;
					}
				}
			}
				if ( $result == true ) {
					print( "success" );
				}
				else {
					print( "Error: Mail Sending Failure" );
				}
			}
		}
	}
}
?>