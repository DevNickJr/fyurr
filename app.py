#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from pydoc import render_doc
from unicodedata import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm 
from flask_wtf import Form
from sqlalchemy import ForeignKey
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable= False)
    city = db.Column(db.String(120), nullable= False)
    state = db.Column(db.String(120), nullable= False)
    address = db.Column(db.String(120), nullable= False)
    phone = db.Column(db.String(120), nullable= False)
    image_link = db.Column(db.String(500), nullable= False)
    facebook_link = db.Column(db.String(120), nullable= False)
    genres =  db.Column(db.ARRAY(db.String()))
    website_link = db.Column(db.String(120)) 
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Venue', lazy=True)

    def __repr__(self) -> str:
       return f'<Venue {self,id}, {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable= False)
    city = db.Column(db.String(120), nullable= False)
    state = db.Column(db.String(120), nullable= False)
    phone = db.Column(db.String(120), nullable= False)
    genres = db.Column(db.String(120), nullable= False)
    image_link = db.Column(db.String(500), nullable= False)
    facebook_link = db.Column(db.String(120), nullable= False)
    genres =  db.Column(db.ARRAY(db.String()))
    website_link = db.Column(db.String(120)) 
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist', lazy=True)

    
    def __repr__(self) -> str:
       return f'<Venue {self,id}, {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#



def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  places = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()  
  for city_state in places:
    city = city_state[0]
    state = city_state[1]
    venues = Venue.query.filter_by(city=city, state=state).all()   
    data.append({
      "city": city,
      "state": state,
      "venues": venues
      })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # name = request.form['name'];
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data = []
  count = 0
  search_term=request.form.get('search_term', '')
  places = Venue.query.with_entities(Venue.name).distinct().all() 
  for names in places:
    name = names[0]
    if search_term.lower() in name.lower():
      venues = Venue.query.filter_by(name=name).all()
      for venue in venues:
        count += 1
        show = Show.query.filter_by(id=venue.id).all()
        data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(show)
        }) 
  response={
    "count": count,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = Venue.query.filter_by(id=venue_id).all()[0]
  return render_template('pages/show_venue.html', venue=data)

  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

  # return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  error = False
  try: 
    venue = Venue(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      address = request.form['address'],
      phone = request.form['phone'],
      genres = request.form.getlist('genres'),
      image_link = request.form['image_link'],
      facebook_link = request.form['facebook_link'],
      website_link = request.form['website_link'],
      seeking_talent = True if 'seeking_talent' in request.form else False, 
      seeking_description = request.form['seeking_description']
    )
    db.session.add(venue)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Venue ' + request.form['name']+ ' could not be listed.')
  if not error: 
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try: 
    data = Venue.query.filter_by(id=venue_id).all()
    # data.delete()
    db.session.delete(data)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Deletion failed')
  if not error: 
    flash('Deleted')
  return render_template('pages/home.html')
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  persons = Artist.query.with_entities(Artist.name, Artist.id).distinct().all()  
  for person in persons:
    name = person[0]
    id = person[1] 
    data.append({
      "name": name,
      "id": id
      })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data = []
  count = 0
  search_term=request.form.get('search_term', '')
  artists = Artist.query.with_entities(Artist.name).distinct().all() 
  for names in artists:
    name = names[0]
    if search_term.lower() in name.lower():
      people = Artist.query.filter_by(name=name).all()
      for person in people:
        count += 1
        show = Show.query.filter_by(id=person.id).all()
        data.append({
        "id": person.id,
        "name": person.name,
        "num_upcoming_shows": len(show)
        }) 
  response={
    "count": count,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data = Artist.query.filter_by(id=artist_id).all()[0]  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm() 
  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  place = Venue.query.filter_by(id = venue_id).all()[0]
  venue={
    "id": place.id,
    "name": place.name,
    "genres": place.genres,
    "address": place.address,
    "city": place.city,
    "state": place.state,
    "phone": place.phone,
    "website": place.website_link,
    "facebook_link": place.facebook_link,
    "seeking_talent": place.seeking_talent,
    "seeking_description": place.seeking_description,
    "image_link": place.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
 
  try: 
    data = Venue.query.filter_by(id=venue_id).all()[0]
    data.name = request.form['name']
    data.city = request.form['city']
    data.state = request.form['state']
    data.address = request.form['address']
    data.phone = request.form['phone']
    data.genres = request.form.getlist('genres')
    data.image_link = request.form['image_link']
    data.facebook_link = request.form['facebook_link']
    data.website_link = request.form['website_link']
    data.seeking_talent = True if 'seeking_talent' in request.form else False
    data.seeking_description = request.form['seeking_description']
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Update failed')
  if not error: 
    flash('Update')
  # return render_template('pages/home.html')
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try: 
    artist = Artist(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      phone = request.form['phone'],
      genres = request.form.getlist('genres'),
      image_link = request.form['image_link'],
      facebook_link = request.form['facebook_link'],
      website_link = request.form['website_link'],
      seeking_talent = True if 'seeking_talent' in request.form else False, 
      seeking_description = request.form['seeking_description']
    )
    db.session.add(artist)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Venue ' + request.form['name']+ ' could not be listed.')
  if not error: 
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Show.query.with_entities(Show.start_time, Show.artist_id, Show.venue_id).distinct().all() 
  for show in shows:
    start_time = show[0]
    artist_id = show[1]
    venue_id = show[2]
    venue = Venue.query.filter_by(id=venue_id).all()[0]   
    artist = Artist.query.filter_by(id=artist_id).all()[0] 
    data.append({
      "start_time": start_time,
      "artist_name": artist.name,
      "venue_name": venue.name
      })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try: 
    show = Show(
      artist_id = request.form['artist_id'],
      venue_id = request.form['venue_id'],
      start_time = request.form['start_time']
    )
    db.session.add(show)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Show ' + ' could not be listed.')
  if not error: 
    flash('Show ' + ' was successfully listed!')
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''


