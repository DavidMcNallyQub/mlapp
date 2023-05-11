import re
"""

"""
class YoutubeVideo:
    """A class representing a YouTube Video."""
    YOUTUBE_VIDEO_ID_LENGTH = 11
    
    """ Note to self about regex expressions:
        (?<name>...) - Allows the substring matched by the group to be accessible via the symbolic group name in <name>
        ^ - Matches the start of the string.
        (?:...) -  Matches whatever regular expression is inside the parentheses, but the substring matched by the group cannot be retrieved after performing a match or referenced later in the pattern. (Non-capturing)
        ? - Causes the resulting Regexp to match 0 or 1 repetitions of the preceding Regexp. ab? will match either 'a' or 'ab'.
        | - A|B, where A and B can be arbitrary REs, creates a regular expression that will match either A or B.
        \ - Either escapes special characters (permitting you to match characters like '*', '?', and so forth), or signals a special sequence; special sequences are discussed below.
        . - In the default mode, this matches any character except a newline.
        + - Causes the resulting RE to match 1 or more repetitions of the preceding RE. ab+ will match 'a' followed by any non-zero number of ‘b’s; it will not match just ‘a’.
        (?!...) - Matches if ... doesn't match next. This is a negative lookahead assertion. For example, Isaac (?!Asimov) will match 'Isaac ' only if it’s not followed by 'Asimov'.  
    """
    
    URL_FORMAT_REGEX_PATTERN = r"""
    (?P<leading_url>                                  # Group accessible by leading_url
        ^(?:https?://|//)?                            #   Optional URL scheme. Either http, or https, or protocol-relative.
        (?:www\.|m\.)?                                #   Optional www or m subdomain.
        (?:                                           #   Group host alternatives:
            youtu\.be/                                #      Either youtu.be,
            |youtube\.com/                            #      or youtube.com
            (?:                                       #      Group path alternatives:
                 embed/                               #        Either /embed/,
                 |v/                                  #        or /v/,
                 |watch\?v=                           #        or /watch?v=,
                 |watch\?.+&v=                        #        or /watch?other_param&v=
            )                                         #      End path alternatives.
        )                                             #   End host alternatives.
    )                                                 # End leading_url group
    (?P<video_id>                                     # Group accessible by video_id
        ([\w-]{"""+str(YOUTUBE_VIDEO_ID_LENGTH)+"""}) #   11 characters (Length of Youtube video ids).
    )                                                 # End video_id group
    (?P<trailing_url>                                 # Group accessible by trailing_url
        (?:.*)                                        #   Any set of characters that isn't a newline.
    )                                                 # End video_id group
    """
    
    def __init__(self, video_url, comments):
        """ Construct a YoutubeVideo instance."""
        self.video_url = video_url
        self.comments = comments
    
    def __str__(self):
        """ Return a YouTubeVideo string respresentation."""
        return f"{self.video_url} : {self.comments} "
    
    @property
    def video_url(self):
        """ The YouTube video URL."""
        return self._video_url
    
    @video_url.setter
    def video_url(self, video_url):
        if re.match(self.URL_FORMAT_REGEX_PATTERN,video_url,re.X):
            self._video_url = video_url
        else:
            raise Exception("The URL does not fit the standard format for a YouTube Video!")
    
    @property
    def video_id(self):
        """ The eleven character YouTube video_id
            
            Each YouTube video's url includes an eleven digit video_id that is unique to that video.      
        """
        return self._segment_url()["video_id"]
    
    @video_id.setter
    def video_id(self,video_id):
        segmented_url = self._segment_url() 
        self._video_url = segmented_url["leading_url"]+video_id+segmented_url["trailing_url"]
    
    def _segment_url(self) -> dict[str,str]:
        """ Return the YouTube Video Id from the videos Url.
        
            For a valid YouTube video URL, the video_id is returned. 
        """
        match = re.match(self.URL_FORMAT_REGEX_PATTERN,self.video_url,re.X)
        if match is None: 
            raise Exception("The URL does not fit the standard format for a YouTube Video!")
        else:
            segmented_url = {}
            segmented_url["leading_url"] = match.group("leading_url")
            segmented_url["video_id"] = match.group("video_id")
            segmented_url["trailing_url"] = match.group("trailing_url")
        return segmented_url 
    
    @property
    def comments(self):
        return self._comments
    
    @comments.setter
    def comments(self,comments):
        #MAYBE NEED TO ADD SOME VALIDATION RULES?
        self._comments = comments
    
    