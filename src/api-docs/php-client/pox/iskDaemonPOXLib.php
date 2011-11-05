<?php

/**
 * Class for communicating with Image DB.
 *
 * Important: Requires package php5-curl installed 
 * (on a Debian system, "sudo apt-get install php5-curl" should be enough)
 *
 * Usage:
 * <code>
 * $imgdb = new ImageDB();
 * $imgdb->addImages( array(
 *      array( 'id' => '1234', 'path' => '/path/to/pic1' ),
 *      array( 'id' => '5678', 'path' => '/path/to/pic2' ),
 *      array( 'id' => '9012', 'path' => '/path/to/pic3' )
 * ) );
 * </code>
 *
 * @package imagedb
 */
class ImageDB {
    const XSI_NAMESPACE = 'http://www.w3.org/2001/XMLSchema-instance';

    const ADD_RESULT_UNKNOWN            = 0;
    const ADD_RESULT_SUCCESS            = 1;
    const ADD_RESULT_ERROR_NOT_UNIQUE   = 2;
    const ADD_RESULT_ERROR_READING_FILE = 3;

    const REMOVE_RESULT_UNKNOWN         = 0;
    const REMOVE_RESULT_SUCCESS         = 1;


    /**
     * Image DB host.
     *
     * @var    string
     * @access private
     */
    private $_host;

     /**
     * Image DB port.
     *
     * @var    integer
     * @access private
     */
    private $_port;

    /**
     * Image DB path.
     *
     * @var    string
     * @access private
     */
    private $_path;

    /**
     * Image DB id.
     *
     * @var    string
     * @access private
     */
    private $_dbid;

    /**
     * CURL timeout.
     *
     * @var    integer
     * @access private
     */
    private $_timeout = 30;


    /**
     * Constructor
     *
     * @throws Exception
     * @access public
     */
    public function __construct( $dbid = '1', $host = 'localhost', $port = 31128, $path = 'isk' ) {
        if ( !function_exists( 'curl_init' ) ) {
            throw new Exception( 'CURL extension not available.' );
        }

        $this->_host = $host;
        $this->_port = $port;
        $this->_path = $path;
        $this->_dbid = $dbid;
    }


    /**
     * Query for similar images.
     *
     * @param  string   $image_id
     * @param  integer  $results
     * @throws Exception
     * @return array
     * @access public
     */
    public function getSimilarImages( $image_id, $results = 20 ) {
        // create dom document
        $document = new DOMDocument( '1.0' );

        // root element
        $image_query = $document->appendChild(
            $document->createElement( 'image_query' )
        );

        $image_query->setAttribute( 'results', $results );
        $image_query->setAttribute( 'dbid', $this->_dbid );
        $image_query->setAttribute( 'type', 1 ); // not in use currently
        $image_query->setAttribute( 'xmlns:xsi', self::XSI_NAMESPACE );
        $image_query->setAttribute( 'xsi:noNamespaceSchemaLocation', 'isk.xsd' );

        // set image
        $image = $image_query->appendChild(
            $document->createElement( 'image' )
        );

        $image->setAttribute( 'id', $image_id );

        // process request
        try {
            $simplexml = $this->_processRequest( $document->saveXML() );
        } catch ( Exception $e ) {
            // rethrow
            throw $e;
        }

        // process response
        $result = array();

        foreach ( $simplexml->result_image as $result_image ) {
            $result[(string)$result_image->image['id']] = number_format( $result_image->ratio, 1 );
        }

        // sort by ratio
        uasort( $result, create_function( '$a, $b', 'return $a < $b;' ) );

        return $result;
    }

    /**
     * Add images.
     *
     * @param  mixed    $in         Either array of strings or string
     * @return boolean
     * @throws Exception
     * @access public
     */
    public function addImages( $in ) {
        if ( is_string( $in ) ) {
            $in = array( $in );
        }

        // create dom document
        $document = new DOMDocument( '1.0' );

        // root element
        $image_query = $document->appendChild(
            $document->createElement( 'new_image_batch' )
        );

        $image_query->setAttribute( 'xmlns:xsi', self::XSI_NAMESPACE );
        $image_query->setAttribute( 'xsi:noNamespaceSchemaLocation', 'isk.xsd' );

        foreach ( $in as $entry ) {
            $image_id   = $entry['id'];
            $image_path = $entry['path'];

            $new_image = $image_query->appendChild(
                $document->createElement( 'new_image' )
            );

            // image element
            $image = $new_image->appendChild(
                $document->createElement( 'image' )
            );

            $image->setAttribute( 'id', $image_id );
            $image->setAttribute( 'dbid', $this->_dbid );

            // path element
            $path = $new_image->appendChild(
                $document->createElement( 'path', $image_path )
            );
        }

        // process request
        try {
            $simplexml = $this->_processRequest( $document->saveXML() );
        } catch ( Exception $e ) {
            // rethrow
            throw $e;
        }

        // process response
        $success = array();

        foreach ( $simplexml->new_image_result as $new_image_result ) {
            switch ( (int)$new_image_result->status ) {
                case self::ADD_RESULT_UNKNOWN:
                case self::ADD_RESULT_ERROR_NOT_UNIQUE:
                case self::ADD_RESULT_ERROR_READING_FILE:
                    break;

                case self::ADD_RESULT_SUCCESS:
                    $success[] = (string)$new_image_result->new_image->image['id'];
                    break;
            }
        }

        return ( count( $in ) == count( $success ) );
    }

    /**
     * Remove images.
     *
     * @param  mixed    $in         Either array of strings or string
     * @return boolean
     * @throws Exception
     * @access public
     */
    public function removeImages( $in ) {
        if ( is_string( $in ) ) {
            $in = array( $in );
        }

        // create dom document
        $document = new DOMDocument( '1.0' );

        // root element
        $image_query = $document->appendChild(
            $document->createElement( 'image_remove_batch' )
        );

        $image_query->setAttribute( 'xmlns:xsi', self::XSI_NAMESPACE );
        $image_query->setAttribute( 'xsi:noNamespaceSchemaLocation', 'isk.xsd' );

        foreach ( $in as $entry ) {
            $image = $image_query->appendChild(
                $document->createElement( 'image' )
            );

            $image->setAttribute( 'id', $entry['id'] );
            $image->setAttribute( 'dbid', $this->_dbid );
        }

        // process request
        try {
            $simplexml = $this->_processRequest( $document->saveXML() );
        } catch ( Exception $e ) {
            // rethrow
            throw $e;
        }

        // process response
        $success = array();

        foreach ( $simplexml->image_remove_result as $remove_result ) {
            switch ( (int)$remove_result->status ) {
                case self::REMOVE_RESULT_UNKNOWN:
                    break;

                case self::REMOVE_RESULT_SUCCESS:
                    $success[] = (string)$remove_result->image['id'];
                    break;
            }
        }

        return ( count( $in ) == count( $success ) );
    }

    // protected methods

    /**
     * Send request.
     *
     * @param  string   $xml
     * @return object               SimpleXML Object
     * @throws Exception
     * @access protected
     */
    protected function _processRequest( $xml ) {
        $url = sprintf( "http://%s:%d/%s",
            $this->_host,
            $this->_port,
            $this->_path
        );

        $ch = curl_init();

        curl_setopt( $ch, CURLOPT_RETURNTRANSFER, 1 );
        curl_setopt( $ch, CURLOPT_VERBOSE, 1 );
        curl_setopt( $ch, CURLOPT_URL, $url );
        curl_setopt( $ch, CURLOPT_TIMEOUT, $this->_timeout );

        curl_setopt( $ch, CURLOPT_POSTFIELDS, $xml );

        curl_setopt( $ch, CURLOPT_POST, 1 );
        $xml = curl_exec( $ch );
        curl_close( $ch );

        // response is xml?
        if ( !preg_match( '/<\?xml(.*)\?>/', $xml ) ) {
            throw new Exception( 'Invalid response.' );
        }

        return simplexml_load_string( $xml );
    }
}

?>
